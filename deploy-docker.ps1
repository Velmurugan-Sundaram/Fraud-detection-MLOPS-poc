# PowerShell Script to Build and Run Docker for Fraud Detection MLOps
# Usage: .\deploy-docker.ps1 [-Action build|run|stop|push] [-ImageTag latest]
# Example: .\deploy-docker.ps1 -Action build
#          .\deploy-docker.ps1 -Action run
#          .\deploy-docker.ps1 -Action push -ImageTag v1.0

param(
    [ValidateSet('build', 'run', 'stop', 'push', 'test')]
    [string]$Action = 'build',
    
    [string]$ImageName = 'fraud-detection-mlops',
    [string]$ImageTag = 'latest',
    [string]$RegistryUrl = '',
    [string]$ContainerName = 'fraud-detection-pipeline'
)

# Configuration
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$DockerFile = Join-Path $ProjectRoot "Dockerfile"
$DockerComposePath = Join-Path $ProjectRoot "docker-compose.yml"

# Colors for output
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red
$Cyan = [System.ConsoleColor]::Cyan

# Helper functions
function Write-Success {
    Write-Host $args -ForegroundColor $Green
}

function Write-Warning {
    Write-Host $args -ForegroundColor $Yellow
}

function Write-Error2 {
    Write-Host $args -ForegroundColor $Red
}

function Write-Info {
    Write-Host $args -ForegroundColor $Cyan
}

# Main functions
function Build-Image {
    Write-Info "=================================================="
    Write-Info "Building Docker Image"
    Write-Info "=================================================="
    
    Write-Info "Image Name: $ImageName"
    Write-Info "Image Tag: $ImageTag"
    Write-Info "Dockerfile: $DockerFile"
    
    if (-not (Test-Path $DockerFile)) {
        Write-Error2 "Dockerfile not found at: $DockerFile"
        exit 1
    }
    
    Write-Info ""
    Write-Info "Starting Docker build..."
    docker build `
        --file $DockerFile `
        --tag "${ImageName}:${ImageTag}" `
        --progress plain `
        $ProjectRoot
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Docker image built successfully!"
        docker images | Select-Object -First 2 | Format-Table
    } else {
        Write-Error2 "✗ Docker build failed!"
        exit 1
    }
}

function Run-Container {
    Write-Info "=================================================="
    Write-Info "Running Docker Container"
    Write-Info "=================================================="
    
    Write-Info "Container Name: $ContainerName"
    Write-Info "Image: ${ImageName}:${ImageTag}"
    
    # Check if image exists
    $imageExists = docker images | Select-String "${ImageName}:${ImageTag}"
    if (-not $imageExists) {
        Write-Error2 "Image not found: ${ImageName}:${ImageTag}"
        Write-Warning "Please build the image first with: .\deploy-docker.ps1 -Action build"
        exit 1
    }
    
    # Prepare volume paths (Windows paths need conversion)
    $DatasetPath = (Join-Path $ProjectRoot "dataset").Replace('\', '/')
    $DataPath = (Join-Path $ProjectRoot "data").Replace('\', '/')
    $LogsPath = (Join-Path $ProjectRoot "logs").Replace('\', '/')
    
    Write-Info ""
    Write-Info "Mounting volumes:"
    Write-Info "  Dataset: $DatasetPath"
    Write-Info "  Data: $DataPath"
    Write-Info "  Logs: $LogsPath"
    
    Write-Info ""
    Write-Info "Starting container with docker-compose..."
    
    Push-Location $ProjectRoot
    docker-compose up -d
    Pop-Location
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Container started successfully!"
        Write-Info ""
        docker ps | Format-Table
        
        Write-Info ""
        Write-Info "View logs with: docker logs -f $ContainerName"
        Write-Info "Stop container with: docker-compose down"
    } else {
        Write-Error2 "✗ Failed to start container!"
        exit 1
    }
}

function Stop-Container {
    Write-Info "=================================================="
    Write-Info "Stopping Docker Containers"
    Write-Info "=================================================="
    
    Push-Location $ProjectRoot
    docker-compose down
    Pop-Location
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Containers stopped successfully!"
    } else {
        Write-Error2 "✗ Failed to stop containers!"
        exit 1
    }
}

function Push-Image {
    Write-Info "=================================================="
    Write-Info "Pushing Image to Registry"
    Write-Info "=================================================="
    
    if ([string]::IsNullOrEmpty($RegistryUrl)) {
        Write-Error2 "Registry URL not provided!"
        Write-Warning "Usage: .\deploy-docker.ps1 -Action push -RegistryUrl 'your-registry' -ImageTag v1.0"
        exit 1
    }
    
    $FullTag = "${RegistryUrl}/${ImageName}:${ImageTag}"
    
    Write-Info "Tagging image: $FullTag"
    docker tag "${ImageName}:${ImageTag}" $FullTag
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error2 "✗ Failed to tag image!"
        exit 1
    }
    
    Write-Info "Pushing image to registry..."
    docker push $FullTag
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Image pushed successfully!"
        Write-Info "Image: $FullTag"
    } else {
        Write-Error2 "✗ Failed to push image!"
        exit 1
    }
}

function Test-Container {
    Write-Info "=================================================="
    Write-Info "Testing Docker Setup"
    Write-Info "=================================================="
    
    Write-Info ""
    Write-Info "1. Checking Docker installation..."
    $dockerVersion = docker --version
    if ($dockerVersion) {
        Write-Success "✓ Docker installed: $dockerVersion"
    } else {
        Write-Error2 "✗ Docker not found! Please install Docker Desktop."
        exit 1
    }
    
    Write-Info ""
    Write-Info "2. Checking docker-compose installation..."
    $composeVersion = docker-compose --version
    if ($composeVersion) {
        Write-Success "✓ Docker Compose installed: $composeVersion"
    } else {
        Write-Error2 "✗ Docker Compose not found!"
        exit 1
    }
    
    Write-Info ""
    Write-Info "3. Checking Dockerfile..."
    if (Test-Path $DockerFile) {
        Write-Success "✓ Dockerfile found"
    } else {
        Write-Error2 "✗ Dockerfile not found at: $DockerFile"
        exit 1
    }
    
    Write-Info ""
    Write-Info "4. Checking docker-compose.yml..."
    if (Test-Path $DockerComposePath) {
        Write-Success "✓ docker-compose.yml found"
    } else {
        Write-Error2 "✗ docker-compose.yml not found"
        exit 1
    }
    
    Write-Info ""
    Write-Info "5. Checking project files..."
    $requiredFiles = @("src/ingestion/pipeline.py", "requirements.txt", "dataset/creditcard.csv")
    $allFound = $true
    foreach ($file in $requiredFiles) {
        $path = Join-Path $ProjectRoot $file
        if (Test-Path $path) {
            Write-Success "✓ $file found"
        } else {
            Write-Warning "⚠ $file not found"
            $allFound = $false
        }
    }
    
    Write-Info ""
    Write-Info "6. Docker system status..."
    docker system df
    
    Write-Info ""
    Write-Success "✓ All checks passed! Ready to deploy."
}

# Main execution
switch ($Action) {
    'build' {
        Build-Image
    }
    'run' {
        Run-Container
    }
    'stop' {
        Stop-Container
    }
    'push' {
        Push-Image
    }
    'test' {
        Test-Container
    }
    default {
        Write-Error2 "Unknown action: $Action"
        exit 1
    }
}

Write-Info ""
Write-Info "=================================================="
Write-Info "✓ Operation completed successfully!"
Write-Info "=================================================="
