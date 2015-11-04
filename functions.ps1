function AddAuditToFile {
    param
    (
        [Parameter(Mandatory=$true)]
        [string]$path
    )
    $path=Resolve-Path($path)
    Get-Acl $path -Audit | Format-List Path,AuditToString | Out-File -FilePath 'file_before.txt' -Width 200 -Append
    $File_ACL = Get-Acl $path
    $AccessRule = New-Object System.Security.AccessControl.FileSystemAuditRule("Everyone","Read”,"none","none",”Success")
    $File_ACL.AddAuditRule($AccessRule)
    $File_ACL | Set-Acl $path
    Get-Acl $path -Audit | Format-List Path,AuditToString | Out-File -FilePath 'file_after.txt' -Width 200 -Append

    $fileObject=(get-item $path)
    if($fileObject){
        $parentFolder=$fileObject.Directory
        Get-Acl $parentFolder -Audit | Format-List Path,AuditToString | Out-File -FilePath 'file_before.txt' -Width 200 -Append
        $File_ACL = Get-Acl $parentFolder
        $AccessRule = New-Object System.Security.AccessControl.FileSystemAuditRule("Everyone","ListDirectory”,"none","none",”Success")
        $File_ACL.AddAuditRule($AccessRule)
        $File_ACL | Set-Acl $parentFolder
        Get-Acl $parentFolder -Audit | Format-List Path,AuditToString | Out-File -FilePath 'file_after.txt' -Width 200 -Append
        }
        else {
        "Couldn't Find Directory of $path"
        }

     
}

function DelAuditFromFile {
    param
    (
        [Parameter(Mandatory=$true)]
        [string]$path
    )
    $path=Resolve-Path($path)
    Get-Acl $path -Audit | Format-List Path,AuditToString | Out-File -FilePath 'file_before_delete.txt' -Width 200 -Append
    $File_ACL = Get-Acl $path
    $AccessRule = New-Object System.Security.AccessControl.FileSystemAuditRule("Everyone","Read”,"none","none",”Success")
    $File_ACL.RemoveAuditRule($AccessRule)
    $File_ACL | Set-Acl $path
    Get-Acl $path -Audit | Format-List Path,AuditToString | Out-File -FilePath 'file_after_delete.txt' -Width 200 -Append


    $parentFolder=(get-item $path).Directory.FullName
    Get-Acl $parentFolder -Audit | Format-List Path,AuditToString | Out-File -FilePath 'file_before.txt' -Width 200 -Append
    $File_ACL = Get-Acl $parentFolder
    $AccessRule = New-Object System.Security.AccessControl.FileSystemAuditRule("Everyone","ListDirectory”,"none","none",”Success,Fail")
    $File_ACL.RemoveAuditRule($parentFolder)
    $File_ACL | Set-Acl $parentFolder
    Get-Acl $parentFolder -Audit | Format-List Path,AuditToString | Out-File -FilePath 'file_after.txt' -Width 200 -Append
}

function AddAuditToRegKey {
    param
    (
        [Parameter(Mandatory=$true)]
        [string]$key
    )

    Get-Acl $key -Audit | Format-List Path,AuditToString | Out-File -FilePath 'reg_before.txt' -Width 200 -Append
    $RegKey_ACL = Get-Acl $key
    $AccessRule = New-Object System.Security.AccessControl.RegistryAuditRule("Everyone","ReadKey”,"none","none",”Success")
    $RegKey_ACL.AddAuditRule($AccessRule)
    $RegKey_ACL | Set-Acl $key
    Get-Acl $key -Audit | Format-List Path,AuditToString | Out-File -FilePath 'reg_after.txt' -Width 200 -Append
}


function DelAuditFromRegKey {
    param
    (
        [Parameter(Mandatory=$true)]
        [string]$key
    )

    Get-Acl $key -Audit | Format-List Path,AuditToString | Out-File -FilePath 'reg_before_delete.txt' -Width 200 -Append
    $RegKey_ACL = Get-Acl $key
    $AccessRule = New-Object System.Security.AccessControl.RegistryAuditRule("Users","ReadKey”,"none","none",”Success")
    $RegKey_ACL.RemoveAuditRule($AccessRule)
    $RegKey_ACL | Set-Acl $key
    Get-Acl $key -Audit | Format-List Path,AuditToString | Out-File -FilePath 'reg_after_delete.txt' -Width 200 -Append
}

function CreateService {
    param
    (
        [Parameter(Mandatory=$true)]
        [string]$serviceName,
        [Parameter(Mandatory=$true)]
        [string]$displayName,
        [Parameter(Mandatory=$true)]
        [string]$binaryPath,
        [Parameter(Mandatory=$true)]
        [string]$description
    )
    
    if (Get-Service $serviceName -ErrorAction SilentlyContinue) {
	    "Service already exists!"
        }
    else {
	    New-Service -name $serviceName -binaryPathName $binaryPath -displayName $displayName -description $description -startupType Automatic
         }

    Start-Service $serviceName
    }


function RemoveService {
    param
    (
        [Parameter(Mandatory=$true)]
        [string]$serviceName       )
    # verify if the service already exists, and if yes remove it
    if (Get-Service $serviceName -ErrorAction SilentlyContinue) {
	    # using WMI to remove Windows service
        $serviceToRemove = Get-WmiObject -Class Win32_Service -Filter "name='$serviceName'"
        $serviceToRemove.delete()
        "service removed"
        }
    else {
	    # just do nothing
        "service does not exists"
     }
     }




