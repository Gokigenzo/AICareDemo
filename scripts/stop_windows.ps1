# ==============================================================================

# AI REHABILITATION & SAFETY ASSISTANT — WINDOWS STOP SCRIPT (POWERSHELL)

# ==============================================================================

# Nhiệm vụ:

# 1. Đọc danh sách PID của Backend Server và Desktop App từ runtime\pids\

# 2. Dừng chính xác các tiến trình do hệ thống Demo sở hữu.

# 3. Tuyệt đối KHÔNG kill hàng loạt python.exe trên máy tính của người dùng.

# 4. Dọn dẹp tệp khóa application.lock và tệp PID.

# ==============================================================================



$ErrorActionPreference = 'SilentlyContinue'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $ScriptDir '..'))



try {

    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8

    [Console]::InputEncoding = [System.Text.Encoding]::UTF8

} catch {}



Write-Host "==================================================================" -ForegroundColor Cyan

Write-Host " 🛑 ĐANG DỪNG HỆ THỐNG AI CARE & REHABILITATION DEMO..." -ForegroundColor Cyan

Write-Host "==================================================================" -ForegroundColor Cyan



$pidsDir = Join-Path $ProjectRoot 'runtime\pids'

$stoppedCount = 0



function Stop-SpecificProcess {

    param([string]$PidFile, [string]$Name)

    if (Test-Path -LiteralPath $PidFile) {

        $pidStr = Get-Content -LiteralPath $PidFile -ErrorAction SilentlyContinue

        if ($pidStr -and ($pidStr -match '^\d+$')) {

            $pidInt = [int]$pidStr

            $p = Get-Process -Id $pidInt -ErrorAction SilentlyContinue

            if ($p) {

                Write-Host " • Đang dừng tiến trình $Name (PID: $pidInt)..." -ForegroundColor Yellow

                # Thử gửi tín hiệu đóng cửa sổ trước

                $closed = $p.CloseMainWindow()

                Start-Sleep -Milliseconds 800

                if (-not $p.HasExited) {

                    $p.Kill()

                }

                Write-Host "   ✅ Đã dừng $Name." -ForegroundColor Green

                $script:stoppedCount++

            } else {

                Write-Host " • Tiến trình $Name (PID: $pidInt) đã kết thúc trước đó." -ForegroundColor Gray

            }

        }

        Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue

    }

}



# 1. Dừng Desktop App

Stop-SpecificProcess (Join-Path $pidsDir 'desktop_app.pid') "Ứng dụng Người cao tuổi (Desktop)"



# 2. Dừng Web Server

Stop-SpecificProcess (Join-Path $pidsDir 'web_server.pid') "Backend Web Server & SSE Gateway"



# 3. Dọn dẹp tệp khóa application.lock

$lockFiles = @(

    (Join-Path $ProjectRoot 'runtime\data\application.lock'),

    (Join-Path $ProjectRoot 'data\application.lock')

)

foreach ($lf in $lockFiles) {

    if (Test-Path -LiteralPath $lf) {

        Remove-Item -LiteralPath $lf -Force -ErrorAction SilentlyContinue

    }

}



Write-Host "`n==================================================================" -ForegroundColor Green

if ($stoppedCount -gt 0) {

    Write-Host " 🎉 ĐÃ DỪNG THÀNH CÔNG TOÀN BỘ TIẾN TRÌNH CỦA BẢN DEMO!" -ForegroundColor Green

} else {

    Write-Host " ℹ️ Không có tiến trình demo nào đang chạy ngầm." -ForegroundColor Green

}

Write-Host "==================================================================`n" -ForegroundColor Green



