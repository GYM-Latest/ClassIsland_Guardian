/* SPDX-License-Identifier: GPL-3.0-only
 * Copyright (C) 2026 GYM_Latest
 */

#include <ntifs.h>

LARGE_INTEGER g_CmCookie = { 0 };

#pragma data_seg("NONPAGED")
// 定义白名单路径
UNICODE_STRING g_guardianExePath = { 0 };
UNICODE_STRING g_configExePath = { 0 };
// 定义保护注册表路径
UNICODE_STRING g_guardianRegPath = { 0 };
UNICODE_STRING g_processRegPath = { 0 };
UNICODE_STRING g_fileRegPath = { 0 };
UNICODE_STRING g_registryRegPath = { 0 };
#pragma data_seg()

NTSTATUS
CIGRegistryCallback(
    _In_ PVOID CallbackContext,
    _In_opt_ PVOID Argument1,
    _In_opt_ PVOID Argument2
);

NTSTATUS DriverEntry(
	_In_ PDRIVER_OBJECT DriverObject,
	_In_ PUNICODE_STRING RegistryPath
);

BOOLEAN IsProcessTrusted(VOID);

NTSTATUS DriverEntry(
	_In_ PDRIVER_OBJECT DriverObject,
	_In_ PUNICODE_STRING RegistryPath
)
{
	UNREFERENCED_PARAMETER(RegistryPath);

    NTSTATUS status;

    // 分配非分页内存并复制字符串
    PWCHAR buffer;

    // guardianExePath
    buffer = (PWCHAR)ExAllocatePool2(POOL_FLAG_NON_PAGED,
        sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\GUARDIAN.EXE"),
        'CIGR');
    if (buffer) {
        RtlCopyMemory(buffer, L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\GUARDIAN.EXE",
            sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\GUARDIAN.EXE"));
        g_guardianExePath.Buffer = buffer;
        g_guardianExePath.Length = (USHORT)(sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\GUARDIAN.EXE") - sizeof(WCHAR));
        g_guardianExePath.MaximumLength = (USHORT)sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\GUARDIAN.EXE");
    }

    // configExePath
    buffer = (PWCHAR)ExAllocatePool2(POOL_FLAG_NON_PAGED,
        sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\CONFIG.EXE"),
        'CIGR');
    if (buffer) {
        RtlCopyMemory(buffer, L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\CONFIG.EXE",
            sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\CONFIG.EXE"));
        g_configExePath.Buffer = buffer;
        g_configExePath.Length = (USHORT)(sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\CONFIG.EXE") - sizeof(WCHAR));
        g_configExePath.MaximumLength = (USHORT)sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\CONFIG.EXE");
    }

    // guardianRegPath
    buffer = (PWCHAR)ExAllocatePool2(POOL_FLAG_NON_PAGED,
        sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\GUARDIAN*"),
        'CIGR');
    if (buffer) {
        RtlCopyMemory(buffer, L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\GUARDIAN*",
            sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\GUARDIAN*"));
        g_guardianRegPath.Buffer = buffer;
        g_guardianRegPath.Length = (USHORT)(sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\GUARDIAN*") - sizeof(WCHAR));
        g_guardianRegPath.MaximumLength = (USHORT)sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\GUARDIAN*");
    }

    // fileRegPath
    buffer = (PWCHAR)ExAllocatePool2(POOL_FLAG_NON_PAGED,
        sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\FILE*"),
        'CIGR');
    if (buffer) {
        RtlCopyMemory(buffer, L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\FILE*",
            sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\FILE*"));
        g_fileRegPath.Buffer = buffer;
        g_fileRegPath.Length = (USHORT)(sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\FILE*") - sizeof(WCHAR));
        g_fileRegPath.MaximumLength = (USHORT)sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\FILE*");
    }

    // processRegPath
    buffer = (PWCHAR)ExAllocatePool2(POOL_FLAG_NON_PAGED,
        sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\PROCESS*"),
        'CIGR');
    if (buffer) {
        RtlCopyMemory(buffer, L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\PROCESS*",
            sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\PROCESS*"));
        g_processRegPath.Buffer = buffer;
        g_processRegPath.Length = (USHORT)(sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\PROCESS*") - sizeof(WCHAR));
        g_processRegPath.MaximumLength = (USHORT)sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\PROCESS*");
    }

    // registryRegPath
    buffer = (PWCHAR)ExAllocatePool2(POOL_FLAG_NON_PAGED,
        sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\REGISTRY*"),
        'CIGR');
    if (buffer) {
        RtlCopyMemory(buffer, L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\REGISTRY*",
            sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\REGISTRY*"));
        g_registryRegPath.Buffer = buffer;
        g_registryRegPath.Length = (USHORT)(sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\REGISTRY*") - sizeof(WCHAR));
        g_registryRegPath.MaximumLength = (USHORT)sizeof(L"\\REGISTRY\\MACHINE\\SYSTEM\\*\\SERVICES\\REGISTRY*");
    }

    UNICODE_STRING altitude;
    RtlInitUnicodeString(&altitude, L"328000.2");

    // 注册 CmRegisterCallbackEx
    status = CmRegisterCallbackEx(
        CIGRegistryCallback,
        &altitude,
        DriverObject,
        NULL,
        &g_CmCookie,
        NULL
    );
    if (!NT_SUCCESS(status)) {
        return status;
    }

	DriverObject->DriverUnload = NULL;
    return STATUS_SUCCESS;
}

// 白名单放行策略
BOOLEAN IsProcessTrusted(VOID) {
    PUNICODE_STRING processPath = NULL;
    if (NT_SUCCESS(SeLocateProcessImageName(PsGetCurrentProcess(), &processPath)) && processPath != NULL) {
        __try {
            UNICODE_STRING saveProcessPath;
            WCHAR saveProcessPath_buf[128];
            RtlInitEmptyUnicodeString(&saveProcessPath, saveProcessPath_buf, 128 * sizeof(WCHAR));
            RtlCopyUnicodeString(&saveProcessPath, processPath);
            if (FsRtlIsNameInExpression(&g_guardianExePath, &saveProcessPath, TRUE, NULL) || FsRtlIsNameInExpression(&g_configExePath, &saveProcessPath, TRUE, NULL)) {
                ExFreePool(processPath);
                return TRUE;
            }
        }
        __except (EXCEPTION_EXECUTE_HANDLER) {
            ;
        }
        ExFreePool(processPath);
    }
    return FALSE;
}

// 拦截策略----------------------------------------------------------
NTSTATUS
CIGRegistryCallback(
    _In_ PVOID CallbackContext,
    _In_opt_ PVOID Argument1,
    _In_opt_ PVOID Argument2
)
{
    UNREFERENCED_PARAMETER(CallbackContext);
    
    // 快速核验
    // 高IRQL下直接放行
    if (Argument2 == NULL) {
        return STATUS_SUCCESS;
    }
    if (KeGetCurrentIrql() > PASSIVE_LEVEL) {
        return STATUS_SUCCESS;
    }

    // 通用拦截
    REG_NOTIFY_CLASS notifyClass = (REG_NOTIFY_CLASS)(ULONG_PTR)(Argument1);
    if (notifyClass == RegNtPreDeleteKey ||
        notifyClass == RegNtPreSetValueKey ||
        notifyClass == RegNtPreDeleteValueKey ||
        notifyClass == RegNtPreRenameKey ||
        notifyClass == RegNtPreSetInformationKey)
    {
        PCUNICODE_STRING keyPath = NULL;
        CmCallbackGetKeyObjectID(
            &g_CmCookie,
            ((PREG_DELETE_KEY_INFORMATION)Argument2)->Object,
            NULL,
            &keyPath);
        if (keyPath != NULL) {
            // F**k you Microsoft
            // 这里微软文档错了害我排查了半天。不要删这里的 (PUNICODE_STRING) 强转
            if (FsRtlIsNameInExpression(&g_guardianRegPath, (PUNICODE_STRING)keyPath, TRUE, NULL) ||
                    FsRtlIsNameInExpression(&g_fileRegPath, (PUNICODE_STRING)keyPath, TRUE, NULL) ||
                    FsRtlIsNameInExpression(&g_processRegPath, (PUNICODE_STRING)keyPath, TRUE, NULL) || 
                    FsRtlIsNameInExpression(&g_registryRegPath, (PUNICODE_STRING)keyPath, TRUE, NULL)) {
                // 白名单进程直接放行
                if (IsProcessTrusted()) {
                    return STATUS_SUCCESS;
                }
                return STATUS_ACCESS_DENIED;
            }
        }
    }

    return STATUS_SUCCESS;
}
