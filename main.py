import flet as ft
import numpy as np

class SLAESolver:
    def __init__(self):
        self.matrix_norm = 0.0
        self.last_error_vector = []

    def make_diagonally_dominant(self, A, b):
        n = len(A)
        new_A = np.zeros((n, n))
        new_b = np.zeros(n)
        
        row_mapping = {} 
        
        used_rows = [False] * n

        for original_idx in range(n):
            row = A[original_idx]
            max_val_idx = np.argmax(np.abs(row))
            
            if max_val_idx not in row_mapping:
                row_mapping[max_val_idx] = original_idx
            else:
                pass

        if len(row_mapping) == n:
            for new_idx in range(n):
                orig_idx = row_mapping[new_idx]
                new_A[new_idx] = A[orig_idx]
                new_b[new_idx] = b[orig_idx]
            
            A = new_A
            b = new_b
            swapped = True
            msg_prefix = "Строки переставлены (максимумы на диагонали). "
        else:
            swapped = False
            msg_prefix = "Перестановка не удалась (конфликт максимумов). "

        is_strict = True
        failed_rows = []
        for i in range(n):
            diag = abs(A[i][i])
            rest_sum = sum(abs(A[i][j]) for j in range(n) if j != i)
            if diag < rest_sum:
                is_strict = False
                failed_rows.append(str(i+1))
        
        if is_strict:
            return A, b, True, "Диагональное преобладание выполнено!"
        else:
            suffix = f"Строгое условие не выполнено в строках: {', '.join(failed_rows)}"
            return A, b, False, msg_prefix + suffix

    def solve_gauss_seidel(self, A, b, eps, max_iter=1000):
        n = len(A)
        x = np.zeros(n, dtype=float)
        x_old = np.copy(x)
        
        self.matrix_norm = np.max(np.sum(np.abs(A), axis=1))
        iteration_errors = []
        converged = False
        steps = 0
        
        for i in range(n):
            if A[i][i] == 0:
                return x, 0, [], False 

        for iteration in range(max_iter):
            steps = iteration + 1
            for i in range(n):
                sum1 = sum(A[i][j] * x[j] for j in range(i))
                sum2 = sum(A[i][j] * x_old[j] for j in range(i+1, n))
                x[i] = (b[i] - sum1 - sum2) / A[i][i]
            
            if np.any(np.abs(x) > 1e10):
                self.last_error_vector = np.abs(x - x_old)
                return x, steps, iteration_errors, False

            current_error_vector = np.abs(x - x_old)
            max_diff = np.max(current_error_vector)
            iteration_errors.append(max_diff)
            
            if max_diff < eps:
                self.last_error_vector = current_error_vector
                converged = True
                break
            
            x_old[:] = x
            
        if not converged:
             self.last_error_vector = np.abs(x - x_old)
             
        return x, steps, iteration_errors, converged



def main(page: ft.Page):
    page.title = "Лаб. 1 - Метод Гаусса-Зейделя (Вариант 16)"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    

    n_val = 3
    matrix_inputs = []
    b_inputs = []
    
    solver = SLAESolver()

    status_text = ft.Text("Ожидание ввода...", color=ft.colors.GREY_700)
    result_container = ft.Column()

    def create_matrix_grid(size):
        matrix_inputs.clear()
        b_inputs.clear()
        grid = ft.Column(spacing=5)
        
        header = ft.Row(controls=[ft.Text("Матрица A", weight="bold", width=size*60), ft.Text("Вектор B", weight="bold")])
        grid.controls.append(header)

        for i in range(size):
            row_controls = ft.Row(spacing=5)
            row_inputs = []
            for j in range(size):
                tf = ft.TextField(
                    value="0" if i != j else "10",
                    width=60, 
                    height=40, 
                    text_align=ft.TextAlign.RIGHT,
                    text_size=14,
                    content_padding=5
                )
                row_inputs.append(tf)
                row_controls.controls.append(tf)
            
            row_controls.controls.append(ft.VerticalDivider(width=10))
            
            b_tf = ft.TextField(value=str(i+1), width=60, height=40, text_align=ft.TextAlign.RIGHT, text_size=14, content_padding=5)
            b_inputs.append(b_tf)
            row_controls.controls.append(b_tf)
            
            matrix_inputs.append(row_inputs)
            grid.controls.append(row_controls)
        
        return grid

    matrix_wrapper = ft.Container(content=create_matrix_grid(n_val))

    def on_n_change(e):
        nonlocal n_val
        try:
            n_val = int(e.control.value)
            matrix_wrapper.content = create_matrix_grid(n_val)
            page.update()
        except:
            pass

    def load_file_result(e: ft.FilePickerResultEvent):
        nonlocal n_val
        
        if not e.files: return
        try:
            with open(e.files[0].path, "r") as f:
                lines = f.readlines()
            
            new_n = int(lines[0].strip())
            
            n_val = new_n
            dd_n.value = str(new_n)
            
            matrix_wrapper.content = create_matrix_grid(new_n)
            

            for i in range(new_n):

                line = lines[i+1].strip()
                if not line: continue 
                
                parts = line.split('|')
                row_vals = list(map(float, parts[0].strip().split()))
                b_val = float(parts[1].strip())
                
                for j in range(new_n):
                    matrix_inputs[i][j].value = str(row_vals[j])
                b_inputs[i].value = str(b_val)
            
            status_text.value = "Файл загружен успешно."
            status_text.color = ft.colors.GREEN
            page.update()
            
        except IndexError:
             status_text.value = "Ошибка: Размерность в файле не совпадает с количеством данных."
             status_text.color = ft.colors.RED
             page.update()
        except Exception as ex:
            status_text.value = f"Ошибка чтения файла: {ex}"
            status_text.color = ft.colors.RED
            page.update()

    def solve_click(e):
        result_container.controls.clear()
        try:
            A = np.zeros((n_val, n_val))
            b = np.zeros(n_val)
            eps = float(eps_field.value)
            
            for i in range(n_val):
                b[i] = float(b_inputs[i].value)
                for j in range(n_val):
                    A[i][j] = float(matrix_inputs[i][j].value)


            A_final, b_final, success, msg = solver.make_diagonally_dominant(A, b)
            
            diag_status = ft.Text(f"Диагональное преобладание: {msg}", 
                                  color=ft.colors.GREEN if success else ft.colors.RED,
                                  weight="bold")
            result_container.controls.append(diag_status)

            if not success:
              
                result_container.controls.append(ft.Text("Попытка решения без преобладания (может не сойтись)...", italic=True))
            
            x, iterations, errors, converged = solver.solve_gauss_seidel(A_final, b_final, eps)
            
            res_col = ft.Column(controls=[
                ft.Divider(),
                ft.Text(f"Норма матрицы: {solver.matrix_norm:.6f}"),
                ft.Text(f"Количество итераций: {iterations}"),
                ft.Text(f"Решение найдено: {'Да' if converged else 'Нет (достигнут лимит)'}", 
                        color=ft.colors.BLUE if converged else ft.colors.RED),
                ft.Divider(),
                ft.Text("Вектор неизвестных (X):", weight="bold"),
                ft.Text(str(np.round(x, 6))),
                ft.Divider(),
                ft.Text("Вектор погрешностей (на посл. итерации):", weight="bold"),
                ft.Text(str(np.round(solver.last_error_vector, 9))),
            ])
            result_container.controls.append(res_col)
            
            status_text.value = "Расчет завершен."
            status_text.color = ft.colors.BLACK

        except ValueError:
            status_text.value = "Ошибка: Проверьте, что во всех ячейках числа."
            status_text.color = ft.colors.RED
        except Exception as ex:
            status_text.value = f"Ошибка: {ex}"
            status_text.color = ft.colors.RED
        
        page.update()

    file_picker = ft.FilePicker(on_result=load_file_result)
    page.overlay.append(file_picker)

    dd_n = ft.Dropdown(
        label="Размерность N", 
        value=str(n_val), 
        options=[ft.dropdown.Option(str(i)) for i in range(2, 21)],
        width=150,
        on_change=on_n_change
    )
    
    eps_field = ft.TextField(label="Точность (ε)", value="0.001", width=150)
    
    top_panel = ft.Row(controls=[
        dd_n, 
        eps_field, 
        ft.ElevatedButton("Загрузить из файла", icon=ft.Icons.UPLOAD_FILE, 
                          on_click=lambda _: file_picker.pick_files(allowed_extensions=["txt"])),
        ft.ElevatedButton("Решить", on_click=solve_click, bgcolor=ft.colors.BLUE, color=ft.colors.WHITE)
    ])

    page.add(
        ft.Text("Решение СЛАУ методом Гаусса-Зейделя", size=20, weight="bold"),
        top_panel,
        status_text,
        ft.Divider(),
        ft.Row(
            controls=[
                ft.Container(content=matrix_wrapper, padding=10, border=ft.border.all(1, ft.colors.GREY_300), border_radius=5),
                ft.Container(content=result_container, padding=10, width=400, alignment=ft.alignment.top_left)
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO
        )
    )

ft.app(target=main)