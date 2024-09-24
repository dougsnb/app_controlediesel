import sys
from cx_Freeze import setup, Executable

# Definindo as opções de build
build_exe_options = {
    "packages": ["os"],
    "includes": ["tkinter"],
    "include_files": []  # Adicione aqui arquivos adicionais, se necessário
}

# Definindo a base
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Para aplicações com interface gráfica no Windows

# Configuração do setup
setup(
    name="Controle de Abastecimento de Diesel",  # Nome do aplicativo
    version="1.0",
    description="Aplicação para controle de abastecimento de diesel.",
    options={"build_exe": build_exe_options},
    executables=[Executable(
        "app.py",  # Altere "seu_codigo.py" para o nome do seu arquivo principal
        base=base,
        target_name="controle_abastecimento.exe",  # Nome do executável gerado
        icon="icone.ico"  # Caminho para o arquivo de ícone .ico
    )]
)
