import flet as ft
import math

class IntegrationMethods:
    
    @staticmethod
    def left_rect(f, a, b, n):
        h = (b - a) / n
        return h * sum(f(a + i * h) for i in range(n))

    @staticmethod
    def right_rect(f, a, b, n):
        h = (b - a) / n
        return h * sum(f(a + i * h) for i in range(1, n + 1))

    @staticmethod
    def mid_rect(f, a, b, n):
        h = (b - a) / n
        return h * sum(f(a + (i + 0.5) * h) for i in range(n))

    @staticmethod
    def trapezoid(f, a, b, n):
        h = (b - a) / n
        s = sum(f(a + i * h) for i in range(1, n))
        return h * (0.5 * (f(a) + f(b)) + s)

    @staticmethod
    def simpson(f, a, b, n):
        if n % 2 != 0:
            n += 1 
        h = (b - a) / n
        s_odd = sum(f(a + i * h) for i in range(1, n, 2))
        s_even = sum(f(a + i * h) for i in range(2, n - 1, 2))
        return (h / 3) * (f(a) + f(b) + 4 * s_odd + 2 * s_even)



METHODS = {
    "Метод левых прямоугольников": (IntegrationMethods.left_rect, 1),
    "Метод правых прямоугольников": (IntegrationMethods.right_rect, 1),
    "Метод средних прямоугольников": (IntegrationMethods.mid_rect, 2),
    "Метод трапеций": (IntegrationMethods.trapezoid, 2),
    "Метод Симпсона": (IntegrationMethods.simpson, 4)
}


FUNCTIONS =[
    {
        "id": 1,
        "name": "1) f(x) = 3x³ - 4x² + 5x - 16 (Обычная, вар. 16)",
        "func": lambda x: 3*x**3 - 4*x**2 + 5*x - 16,
        "singularity": None,
        "converges": True
    },
    {
        "id": 2,
        "name": "2) f(x) = sin(x) / x (Устранимый разрыв)",
        "func": lambda x: math.sin(x)/x if x != 0 else 1.0,
        "singularity": None,
        "converges": True
    },
    {
        "id": 3,
        "name": "3) f(x) = 1 / sqrt(x) (Разрыв в x=0, левая граница. Сходится)",
        "func": lambda x: 1 / math.sqrt(x),
        "singularity": 0.0,
        "converges": True
    },
    {
        "id": 4,
        "name": "4) f(x) = 1 / x² (Разрыв в x=0. Расходится)",
        "func": lambda x: 1 / (x**2),
        "singularity": 0.0,
        "converges": False
    },
    {
        "id": 5,
        "name": "5) f(x) = 1 / sqrt(2 - x) (Разрыв в x=2, правая граница. Сходится)",
        "func": lambda x: 1 / math.sqrt(2 - x),
        "singularity": 2.0,
        "converges": True
    },
    {
        "id": 6,
        "name": "6) f(x) = 1 / sqrt(|x - 1|) (Разрыв в x=1, внутри. Сходится)",
        "func": lambda x: 1 / math.sqrt(abs(x - 1)),
        "singularity": 1.0,
        "converges": True
    }
]

def compute_integral(func_dict, a, b, eps, method_name):
    method, k = METHODS[method_name]
    f = func_dict["func"]
    singularity = func_dict["singularity"]
    converges = func_dict["converges"]

    # Проверка на сходимость, если особая точка попала в отрезок
    if singularity is not None and min(a, b) <= singularity <= max(a, b):
        if not converges:
            return None, "Интеграл не существует (расходится)."

    # Обработка точек разрыва (Необязательное задание)
    delta = 1e-6 # бесконечно малый отступ, чтобы не делить на ноль
    intervals =[]
    
    if singularity is not None and min(a, b) <= singularity <= max(a, b):
        if abs(a - singularity) < 1e-9:
            intervals.append((a + delta, b))
        elif abs(b - singularity) < 1e-9:
            intervals.append((a, b - delta))
        else:
            intervals.append((a, singularity - delta))
            intervals.append((singularity + delta, b))
    else:
        intervals.append((a, b))

    total_integral = 0
    total_n = 0


    for (start, end) in intervals:
        if start >= end: continue
        
        n = 4 
        I_n = method(f, start, end, n)
        
        while True:
            I_2n = method(f, start, end, 2 * n)
            
            # Правило Рунге
            error = abs(I_2n - I_n) / (2**k - 1)
            
            if error <= eps:
                total_integral += I_2n
                total_n += (2 * n)
                break
                
            n *= 2
            
            if n > 1000000:
                return None, f"Не удалось достичь требуемой точности. Остановлено на n={n}."
            
            I_n = I_2n

    return total_integral, total_n


def main(page: ft.Page):
    page.title = "Численное интегрирование"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 750
    page.window_height = 650
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO


    func_dropdown = ft.Dropdown(
        label="Выберите функцию",
        options=[ft.dropdown.Option(text=f["name"], key=str(f["id"])) for f in FUNCTIONS],
        width=600,
        value="1"
    )

    method_dropdown = ft.Dropdown(
        label="Метод интегрирования",
        options=[ft.dropdown.Option(text=m) for m in METHODS.keys()],
        width=300,
        value="Метод Симпсона"
    )

    a_input = ft.TextField(label="Нижний предел (a)", width=150, value="2")
    b_input = ft.TextField(label="Верхний предел (b)", width=150, value="4")
    eps_input = ft.TextField(label="Точность (ε)", width=150, value="0.001")

    result_text = ft.Text("Ожидание ввода...", size=18, weight="w600", color=ft.colors.BLUE_200)


    def calculate(e):
        result_text.color = ft.colors.WHITE
        result_text.value = "Считаем..."
        page.update()

        try:
            a = float(a_input.value)
            b = float(b_input.value)
            eps = float(eps_input.value)
        except ValueError:
            result_text.value = "Ошибка: Пределы и точность должны быть числами!"
            result_text.color = ft.colors.RED
            page.update()
            return

        if eps <= 0:
            result_text.value = "Ошибка: точность должна быть больше 0"
            result_text.color = ft.colors.RED
            page.update()
            return

        func_id = int(func_dropdown.value)
        func_dict = next(f for f in FUNCTIONS if f["id"] == func_id)
        method_name = method_dropdown.value


        sign = 1
        if a > b:
            a, b = b, a
            sign = -1
        elif a == b:
            result_text.value = "Результат: 0 (пределы интегрирования равны)"
            result_text.color = ft.colors.YELLOW
            page.update()
            return

        try:
            res, n = compute_integral(func_dict, a, b, eps, method_name)
            
            if res is None:
                result_text.value = f"⚠️ {n}"
                result_text.color = ft.colors.AMBER_400
            else:
                res *= sign
                result_text.value = (
                    f"Успешно вычислено!\n\n"
                    f"Значение интеграла: {res:.7f}\n"
                    f"Число разбиений (n): {n}\n"
                    f"Точность достигнута: {eps}"
                )
                result_text.color = ft.colors.GREEN_400
                
        except Exception as ex:
            result_text.value = f"Произошла ошибка вычисления: {ex}"
            result_text.color = ft.colors.RED
            
        page.update()

    calc_btn = ft.ElevatedButton("Вычислить", on_click=calculate, icon=ft.icons.CALCULATE, height=50)

    page.add(
        ft.Text("Лабораторная работа №3", size=26, weight="bold"),
        ft.Text("Численное интегрирование (Вариант 16)", size=16, color=ft.colors.GREY_400),
        ft.Divider(height=20, color=ft.colors.TRANSPARENT),
        
        func_dropdown,
        ft.Container(height=10),
        
        ft.Row([a_input, b_input, eps_input], spacing=20),
        ft.Container(height=10),
        
        method_dropdown,
        ft.Container(height=20),
        
        calc_btn,
        ft.Divider(height=30, color=ft.colors.GREY_800),
        
        ft.Container(
            content=result_text,
            padding=20,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=10,
            width=600
        )
    )

if __name__ == "__main__":
    ft.app(target=main)