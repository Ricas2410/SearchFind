# PowerShell script to install AI dependencies for SearchFind
# This script activates the virtual environment and runs the Python installation script

# Define colors for output messages
$ForegroundColors = @{
    "Info" = "Cyan"
    "Success" = "Green"
    "Error" = "Red"
}

# Function to write colored output
function Write-ColorOutput {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $true)]
        [string]$Type
    )

    Write-Host $Message -ForegroundColor $ForegroundColors[$Type]
}

# Welcome message
Write-ColorOutput "Starting SearchFind AI dependencies installation..." "Info"
Write-ColorOutput "This script will activate the virtual environment and install required packages." "Info"

# Check if venv directory exists
if (-Not (Test-Path -Path "venv")) {
    Write-ColorOutput "Virtual environment not found. Creating a new one..." "Info"
    
    try {
        python -m venv venv
        Write-ColorOutput "Virtual environment created successfully." "Success"
    }
    catch {
        Write-ColorOutput "Failed to create virtual environment. Error: $_" "Error"
        Write-ColorOutput "Please create the virtual environment manually with: python -m venv venv" "Error"
        exit 1
    }
}

# Activate virtual environment and run the installation script
Write-ColorOutput "Activating virtual environment and installing dependencies..." "Info"

try {
    # Using semicolons as requested by the user (instead of &&)
    $activateCommand = ".\venv\Scripts\Activate.ps1; python scripts\install_ai_dependencies.py"
    
    # Execute the PowerShell command
    Invoke-Expression $activateCommand
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "AI dependencies installation completed successfully!" "Success"
        Write-ColorOutput "You can now use the AI features in SearchFind." "Success"
    }
    else {
        Write-ColorOutput "Installation script exited with code $LASTEXITCODE" "Error"
        Write-ColorOutput "Please check the error messages above and try again." "Error"
    }
}
catch {
    Write-ColorOutput "An error occurred during installation: $_" "Error"
    Write-ColorOutput "Please try running the commands manually:" "Error"
    Write-ColorOutput "1. .\venv\Scripts\Activate.ps1" "Info"
    Write-ColorOutput "2. python scripts\install_ai_dependencies.py" "Info"
    exit 1
}

# Final instructions
Write-ColorOutput "`nNext steps:" "Info"
Write-ColorOutput "1. Make sure the virtual environment is activated before running SearchFind" "Info"
Write-ColorOutput "2. Test the AI features with sample documents" "Info"
Write-ColorOutput "3. Review the implementation status in subscriptions/AI_IMPLEMENTATION_STATUS.md" "Info"

# Press any key to exit
Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")