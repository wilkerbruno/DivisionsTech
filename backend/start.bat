@echo off
cd /d "%~dp0"

echo.
echo   ==========================================
echo     Divisions Tech -- Backend v2.0
echo   ==========================================
echo.

echo [1/3] Instalando dependencias...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERRO ao instalar dependencias. Verifique se o Python esta instalado.
    pause
    exit /b 1
)
echo        OK

echo.
echo [2/3] Criando tabelas no MySQL...
python create_tables.py
if errorlevel 1 (
    echo ERRO ao criar tabelas. Verifique a conexao com o MySQL em config.py
    pause
    exit /b 1
)

echo.
echo [3/3] Iniciando servidor na porta 8000...
echo        Documentacao: http://localhost:8000/docs
echo.
python main.py
pause
