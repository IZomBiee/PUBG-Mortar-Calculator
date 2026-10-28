uv run pyinstaller `
    --name "PUBG-Mortar-Calculator" `
    --onedir `
    --noconfirm `
    --paths . `
    --icon "assets/icon.ico" `
    --collect-all customtkinter `
    --collect-binaries onnxruntime `
    --collect-data onnxruntime `
    --exclude-module torch `
    --exclude-module torchvision `
    --exclude-module matplotlib `
    --exclude-module scipy `
    --add-data "assets;assets" `
    pubg_mortar_calculator/__main__.py