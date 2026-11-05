import os
import argparse
import platform
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

def find_chrome():
    system = platform.system()

    if system == "Darwin":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]

    elif system == "Windows":
        candidates = [
            str(Path(os.environ.get("PROGRAMFILES", "C:/Program Files"))
                / "Google/Chrome/Application/chrome.exe"),
            str(Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)"))
                / "Google/Chrome/Application/chrome.exe"),
            str(Path(os.environ.get("LOCALAPPDATA", ""))
                / "Google/Chrome/Application/chrome.exe"),
        ]

    elif system == "Linux":
        for name in ["google-chrome", "google-chrome-stable",
                     "chromium", "chromium-browser"]:
            path = shutil.which(name)
            if path:
                return path

        candidates = []

    else:
        raise RuntimeError(f"Unsupported OS: {system}")

    for path in candidates:
        if Path(path).is_file():
            return path

    raise RuntimeError("Google Chrome not found")

def leer_archivo_entrada(filename):
    """Lee las líneas: legajo nota archivo."""

    assignments = []

    with open(filename, encoding="utf-8") as f:
        for number, line in enumerate(f, start=1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split(maxsplit=2)

            if len(parts) != 3:
                raise ValueError(
                    f"Línea {number} inválida. "
                    "Se esperaba: legajo nota archivo"
                )

            legajo, nota, filename = parts
            attachment = Path(filename)

            if not attachment.is_absolute():
                attachment = Path.cwd() / attachment

            if not attachment.is_file():
                raise FileNotFoundError(
                    f"Línea {number}: no existe el archivo {attachment}"
                )

            assignments.append((legajo, nota, attachment))

    return assignments


def seleccionar_actividad(page, nombre_actividad):
    """Filtra el libro de calificaciones por actividad."""

    page.locator(
        '[data-analytics-id="component.gradebook.view.toolbar.filter"]'
    ).click()

    column_picker = page.locator("#columns-picker")
    column_picker.click()

    page.locator("#columns-picker-search-box").fill(nombre_actividad)

    option = page.locator(
        '[data-analytics-id="component.gradebook.view.toolbar.filter.columnsPicker.pickColumns.columnsPicker.listbox"]'
    )

    if "No hay elementos calificables" in option.inner_text():
        raise Exception(f"Actividad {nombre_actividad} no encontrada")

    option.click()
    column_picker.click()

    page.locator(
        '[data-analytics-id="component.gradebook.view.toolbar.filter.apply"]'
    ).click()


def buscar_alumno(page, legajo):
    """Busca un alumno por legajo. Devuelve False si no existe."""

    boton = page.locator('button[aria-label="Borrar búsqueda"]')

    if boton.is_visible():
        boton.click()
    
    page.locator(
        '[data-analytics-id="component.gradebook.view.toolbar.search"]'
    ).fill(legajo)

    option = page.locator(
        "#gradebook-grid-search-items-input-dropdown-option-0"
    )

    if "No se encontraron resultados" in option.inner_text():
        print(f"Legajo {legajo} no encontrado")
        return False

    option.click()
    return True


def actualizar_nota(page, nota):
    """Actualiza la nota del alumno seleccionado."""

    page.locator(
        '[data-analytics-id="course.grade.gradebook.gridview.columnEditButton"]'
    ).click(force=True)

    page.locator(
        '[data-analytics-id="course.grade.gradebook.gridview.editableGradeCell.gradeInput"] input'
    ).fill(nota)

    page.locator(
        '[data-analytics-id="course.grade.gradebook.gridview.columnConfirmButton"]'
    ).click()


def adjuntar_feedback(page, legajo, attachment):
    """Adjunta el archivo al feedback general del alumno."""

    page.locator(
        '[data-analytics-id="course.grade.gradebook.gridview.gradeCell.action"]'
    ).click()

    page.locator(
        '[data-analytics-id="course.grade.gradebook.gridview.sidebar.gradeDetail.assessment.assessmentFeedback.accordion.expansionPanelSummary"]'
    ).click()

    edit_feedback = page.locator(
        '[data-analytics-id="course.grade.gradebook.gridview.sidebar.gradeDetail.assessment.assessmentFeedback.overallFeedback.editOverallFeedback.content.edit"]'
    )

    if edit_feedback.count() > 0:

        adjunto = page.locator('[data-bbtype="attachment"]')

        if adjunto.count() > 0:
            nombre = adjunto.locator('.js-file-viewer-attachment-meta span').inner_text()

            if nombre != os.path.basename(attachment):
                print(f"Ya existe un adjunto diferente ({nombre}) para {legajo}")
            else:
                print(f"{nombre} ya está adjunto para {legajo}")


            page.locator(
                '[data-analytics-id="course.grade.gradebook.gridview.sidebar.gradeDetail.header.close"]'
            ).click()

            return

        edit_feedback.click()

    else:
        page.locator(
            '[data-analytics-id="course.grade.gradebook.gridview.sidebar.gradeDetail.assessment.assessmentFeedback.overallFeedback.addFeedback"]'
        ).click()

    # Insertar archivo
    page.locator(
        '[data-analytics-id="editor.toolbar.insertContent.button"]'
    ).click()

    with page.expect_file_chooser() as fc_info:
        page.locator(
            '[data-analytics-id="editor.toolbar.insertLocalFile.button"]'
        ).click()

    file_chooser = fc_info.value
    file_chooser.set_files(str(attachment))

    # Guardar archivo
    page.locator(
        '[data-analytics-id="editor.modelEditAttachment.dialogFooter.save.button"]'
    ).click()

    # Guardar feedback
    page.locator(
        '[data-analytics-id="course.grade.gradebook.gridview.sidebar.gradeDetail.assessment.assessmentFeedback.overallFeedback.saveButton"]'
    ).click()

    print(f"Adjunto cargado para {legajo}: {attachment.name}")

    page.locator(
        '[data-analytics-id="course.grade.gradebook.gridview.sidebar.gradeDetail.header.close"]'
    ).click()

def procesar_alumno(page, legajo, nota, attachment):
    """Busca al alumno, actualiza su nota y adjunta el archivo."""

    if not buscar_alumno(page, legajo):
        return

    actualizar_nota(page, nota)
    adjuntar_feedback(page, legajo, attachment)


def main():
    parser = argparse.ArgumentParser(
        description="Actualiza notas y adjunta archivos en Blackboard."
    )

    parser.add_argument("actividad", help="Nombre de la actividad")
    parser.add_argument("archivo", help="Archivo con legajos, notas y rutas a archivos a adjuntar")

    args = parser.parse_args()

    assignments = leer_archivo_entrada(args.archivo)

    if not assignments:
        raise Exception("El archivo de entrada no contiene alumnos.")

    print(f"Alumnos a procesar: {len(assignments)}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="./blackboard_profile",
            executable_path=find_chrome(),
            headless=False,
            slow_mo=200
        )

        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.set_default_timeout(10000)

            page.goto("https://campus.itba.edu.ar/")

            print(
                "Iniciar sesión y navegar hasta el libro de "
                "calificaciones del curso correspondiente"
            )

            page.wait_for_function(
                "document.title.includes('Libro de calificaciones')",
                timeout=60000
            )

            seleccionar_actividad(page, args.actividad)

            for legajo, nota, attachment in assignments:
                print(f"\nProcesando legajo {legajo} (nota: {nota})")

                procesar_alumno(page, legajo, nota, attachment)

        finally:
            context.close()


if __name__ == "__main__":
    main()
