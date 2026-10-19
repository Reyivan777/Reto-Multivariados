# Renderiza el archivo Rmd/Qmd activo de RStudio y guarda el HTML en html_files/

repo_root <- tryCatch(
  trimws(system2("git", c("rev-parse", "--show-toplevel"), stdout = TRUE)),
  error = function(e) getwd()
)

if (length(repo_root) == 0 || !nzchar(repo_root[1])) repo_root <- getwd()
repo_root <- normalizePath(repo_root[1], winslash = "/", mustWork = TRUE)
out_dir <- file.path(repo_root, "html_files")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

if (!requireNamespace("rstudioapi", quietly = TRUE)) {
  stop("Instala rstudioapi con install.packages('rstudioapi').")
}

# Obtiene el archivo activo del editor, aunque la consola tenga el foco.
input <- rstudioapi::getSourceEditorContext()$path
if (!nzchar(input)) stop("Abre y guarda primero el archivo .Rmd o .qmd que quieres renderizar.")

ext <- tolower(tools::file_ext(input))

if (ext == "rmd") {
  if (!requireNamespace("rmarkdown", quietly = TRUE)) {
    stop("Instala rmarkdown con install.packages('rmarkdown').")
  }

  rmarkdown::render(
    input = input,
    output_format = "html_document",
    output_dir = out_dir,
    envir = new.env(parent = globalenv())
  )

} else if (ext == "qmd") {
  quarto_bin <- Sys.which("quarto")
  if (!nzchar(quarto_bin)) stop("No se encontró Quarto en el sistema.")

  status <- system2(
    quarto_bin,
    c("render", shQuote(input), "--to", "html", "--output-dir", shQuote(out_dir))
  )

  if (status != 0) stop("Quarto no pudo renderizar el archivo.")

} else {
  stop("El archivo activo debe ser .Rmd o .qmd.")
}

message("HTML guardado en: ", out_dir)
