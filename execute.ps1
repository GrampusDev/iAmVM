    param
    (
        [Parameter(Mandatory=$true)]
        [string]$action
    )

. ./functions.ps1
$iniConf=Get-IniContent .\iAmVM_conf.ini
$fileNames=$iniConf.Paths.fileNames.ToString()
$regKeysPath=$iniConf.Paths.regKeysPath.ToString()
if ($action -eq "Install") {
    "Script is Running... Please Wait.."
	$filesToAudit=Get-Content .\$fileNames
	foreach ($file in $filesToAudit) {
    		AddAuditToFile $file
	}

	$keysToAudit=Get-Content .\$regKeysPath
	foreach ($key in $keysToAudit) {
    	AddAuditToRegKey $key
	}

    $serviceName = "VBoxService"
    $displayName = "VirtualBox Guest Additions Service"
    $binaryPath = "system32\VBoxService.exe"
    $description = "Manages VM runtime information, time synchronization, remote sysprep execution and miscellaneous utilities for guest operating systems."
    CreateService $serviceName $displayName $binaryPath $description


    auditpol.exe /set /subcategory:"File System" /success:enable /failure:enable
    auditpol.exe /set /subcategory:"Registry" /success:enable /failure:enable
    auditpol.exe /get /category:"Object Access"| Out-File -FilePath "audit_policies_after_install.txt"
    } 
else { 

	$filesToAudit=Get-Content .\Files.txt
	foreach ($file in $filesToAudit) {
	    DelAuditFromFile $file
	    "$file"
	} 


	$keysToAudit=Get-Content .\Reg.txt
	foreach ($key in $keysToAudit) {
	    DelAuditFromRegKey $key
	    "$key"
	}

    $serviceName = "VBoxService"
    RemoveService($serviceName)

    auditpol.exe /set /subcategory:"File System" /success:disable /failure:disable
    auditpol.exe /set /subcategory:"Registry" /success:disable /failure:disable
    auditpol.exe /get /category:"Object Access"| Out-File -FilePath "audit_policies_after_remove.txt"
    }