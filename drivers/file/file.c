/*
 * SPDX-License-Identifier: GPL-3.0-only
 * Copyright (C) 2026 GYM_Latest
 */

#include <fltKernel.h>
#include <dontuse.h>
#include <suppress.h>

#pragma prefast(disable:__WARNING_ENCODE_MEMBER_FUNCTION_POINTER, "Not valid for kernel mode drivers")

// 定义保护与白名单路径
#pragma data_seg("NONPAGED")
// 白名单
UNICODE_STRING g_guardianExePath = { 0 };
UNICODE_STRING g_configExePath = { 0 };
// 保护
UNICODE_STRING g_guardianRecoveryPath = { 0 };
UNICODE_STRING g_guardianPath = { 0 };
#pragma data_seg()

// 手动定义 FileRenameInformationEx 结构体
#if !defined(FILE_RENAME_INFORMATION_EX_DEFINED)
#define FILE_RENAME_INFORMATION_EX_DEFINED

typedef struct _FILE_RENAME_INFORMATION_EX {
    BOOLEAN ReplaceIfExists;
    HANDLE  RootDirectory;
    ULONG   FileNameLength;
    ULONG   Flags;
    WCHAR   FileName[1];
} FILE_RENAME_INFORMATION_EX, * PFILE_RENAME_INFORMATION_EX;

#endif

typedef struct _CIGFile_FILTER_DATA {

    PFLT_FILTER FilterHandle;

} CIGFile_FILTER_DATA, * PCIGFILE_FILTER_DATA;

DRIVER_INITIALIZE DriverEntry;
NTSTATUS
DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
);

NTSTATUS
CIGFileUnload(
    _In_ FLT_FILTER_UNLOAD_FLAGS Flags
);

NTSTATUS
CIGFileQueryTeardown(
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _In_ FLT_INSTANCE_QUERY_TEARDOWN_FLAGS Flags
);

CIGFile_FILTER_DATA CIGFileFilterData;

#ifdef ALLOC_PRAGMA
#pragma alloc_text(INIT, DriverEntry)
#pragma alloc_text(PAGE,   CIGFileUnload)
#pragma alloc_text(PAGE, CIGFileQueryTeardown)
#endif

// 添加写入回调函数
FLT_PREOP_CALLBACK_STATUS
CIGPreWrite(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Out_ PVOID* CompletionContext
);

// 添加读取回调函数
FLT_PREOP_CALLBACK_STATUS
CIGPreRead(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Out_ PVOID* CompletionContext
);


// 定义操作回调表-全部拦截
CONST FLT_OPERATION_REGISTRATION Callbacks[] = {
    { IRP_MJ_CREATE, 0, CIGPreWrite, NULL },  // 打开/创建
    { IRP_MJ_READ, 0, CIGPreRead, NULL },  // 读取
    { IRP_MJ_WRITE, 0, CIGPreWrite, NULL },  // 写入
    { IRP_MJ_SET_INFORMATION, 0, CIGPreWrite, NULL },  // 删除/重命名/改属性
    { IRP_MJ_DIRECTORY_CONTROL,0,  CIGPreRead, NULL },  // 遍历目录（列举文件）
    { IRP_MJ_OPERATION_END }
};

CONST FLT_REGISTRATION FilterRegistration = {

    sizeof(FLT_REGISTRATION),         //  Size
    FLT_REGISTRATION_VERSION,           //  Version
    0,                                  //  Flags

    NULL,                               //  Context
    Callbacks,                               //  Operation callbacks

    CIGFileUnload,                         //  FilterUnload

    NULL,                               //  InstanceSetup
    CIGFileQueryTeardown,                  //  InstanceQueryTeardown
    NULL,                               //  InstanceTeardownStart
    NULL,                               //  InstanceTeardownComplete

    NULL,                               //  GenerateFileName
    NULL,                               //  GenerateDestinationFileName
    NULL                                //  NormalizeNameComponent

};

NTSTATUS
DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
)
{
    NTSTATUS status;

    UNREFERENCED_PARAMETER(RegistryPath);

    // 分配非分页内存并复制字符串
    PWCHAR buffer;

    // guardianRecoveryPath
    buffer = (PWCHAR)ExAllocatePool2(POOL_FLAG_NON_PAGED,
        sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\GUARDIANRECOVERY*"),
        'CIGP');
    if (buffer) {
        RtlCopyMemory(buffer, L"\\DEVICE\\HARDDISKVOLUME*\\GUARDIANRECOVERY*",
            sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\GUARDIANRECOVERY*"));
        g_guardianRecoveryPath.Buffer = buffer;
        g_guardianRecoveryPath.Length = (USHORT)(sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\GUARDIANRECOVERY*") - sizeof(WCHAR));
        g_guardianRecoveryPath.MaximumLength = (USHORT)sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\GUARDIANRECOVERY*");
    }

    // guardianPath
    buffer = (PWCHAR)ExAllocatePool2(POOL_FLAG_NON_PAGED,
        sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN*"),
        'CIGP');
    if (buffer) {
        RtlCopyMemory(buffer, L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN*",
            sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN*"));
        g_guardianPath.Buffer = buffer;
        g_guardianPath.Length = (USHORT)(sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN*") - sizeof(WCHAR));
        g_guardianPath.MaximumLength = (USHORT)sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN*");
    }

    // guardianExePath
    buffer = (PWCHAR)ExAllocatePool2(POOL_FLAG_NON_PAGED,
        sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\GUARDIAN.EXE"),
        'CIGP');
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
        'CIGP');
    if (buffer) {
        RtlCopyMemory(buffer, L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\CONFIG.EXE",
            sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\CONFIG.EXE"));
        g_configExePath.Buffer = buffer;
        g_configExePath.Length = (USHORT)(sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\CONFIG.EXE") - sizeof(WCHAR));
        g_configExePath.MaximumLength = (USHORT)sizeof(L"\\DEVICE\\HARDDISKVOLUME*\\PROGRAM FILES\\GUARDIAN\\CONFIG.EXE");
    }

    status = FltRegisterFilter(DriverObject,
        &FilterRegistration,
        &CIGFileFilterData.FilterHandle);

    FLT_ASSERT(NT_SUCCESS(status));

    if (NT_SUCCESS(status)) {
        status = FltStartFiltering(CIGFileFilterData.FilterHandle);

        if (!NT_SUCCESS(status)) {
            FltUnregisterFilter(CIGFileFilterData.FilterHandle);
        }
    }
    return status;
}

NTSTATUS
CIGFileUnload(
    _In_ FLT_FILTER_UNLOAD_FLAGS Flags
)
{
    UNREFERENCED_PARAMETER(Flags);

    PAGED_CODE();

    FltUnregisterFilter(CIGFileFilterData.FilterHandle);

    if (g_guardianRecoveryPath.Buffer) ExFreePool(g_guardianRecoveryPath.Buffer);
    if (g_guardianPath.Buffer)          ExFreePool(g_guardianPath.Buffer);
    if (g_guardianExePath.Buffer)       ExFreePool(g_guardianExePath.Buffer);
    if (g_configExePath.Buffer)         ExFreePool(g_configExePath.Buffer);

    return STATUS_SUCCESS;
}

NTSTATUS
CIGFileQueryTeardown(
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _In_ FLT_INSTANCE_QUERY_TEARDOWN_FLAGS Flags
)
{
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(Flags);

    PAGED_CODE();

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

// 写入拦截策略----------------------------------------------------------
FLT_PREOP_CALLBACK_STATUS
CIGPreWrite(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Out_ PVOID* CompletionContext
)
{
    *CompletionContext = NULL;

     // 快速核验
    // 高IRQL下直接放行
    if (KeGetCurrentIrql() > PASSIVE_LEVEL) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    UCHAR majorFunction = Data->Iopb->MajorFunction;
    // 判断是否为打开
    if (majorFunction == IRP_MJ_CREATE) {
        ULONG createDisposition = (Data->Iopb->Parameters.Create.Options >> 24) & 0xFF;
        if (createDisposition == FILE_OPEN) {
            return FLT_PREOP_SUCCESS_NO_CALLBACK;
        }
    }
    // 判断是否为移动
    if (majorFunction == IRP_MJ_SET_INFORMATION) {
        FILE_INFORMATION_CLASS infoClass = Data->Iopb->Parameters.SetFileInformation.FileInformationClass;
        if (infoClass == FileRenameInformation || infoClass == FileRenameInformationEx) {
            UNICODE_STRING targetFileName = { 0 };
            HANDLE rootDir = NULL;
            PVOID infoBuffer = Data->Iopb->Parameters.SetFileInformation.InfoBuffer;
            if (infoClass == FileRenameInformation) {
                PFILE_RENAME_INFORMATION pInfo = (PFILE_RENAME_INFORMATION)infoBuffer;
                rootDir = pInfo->RootDirectory;
                targetFileName.Buffer = pInfo->FileName;
                targetFileName.Length = (USHORT) pInfo->FileNameLength;
                targetFileName.MaximumLength = (USHORT) pInfo->FileNameLength;
            }
            else {
                PFILE_RENAME_INFORMATION_EX pInfoEx = (PFILE_RENAME_INFORMATION_EX)infoBuffer;
                rootDir = pInfoEx->RootDirectory;
                targetFileName.Buffer = pInfoEx->FileName;
                targetFileName.Length = (USHORT) pInfoEx->FileNameLength;
                targetFileName.MaximumLength = (USHORT) pInfoEx->FileNameLength;
            }
            PFLT_FILE_NAME_INFORMATION targetInfo = NULL;
            NTSTATUS status = FltGetDestinationFileNameInformation(
                FltObjects->Instance,
                FltObjects->FileObject,
                rootDir,
                targetFileName.Buffer,
                targetFileName.Length,
                FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT,
                &targetInfo
            );
            if (!NT_SUCCESS(status)) {
                // 仅放行极少数卷卸载，其余一律拒绝
                if (status == STATUS_FLT_DELETING_OBJECT || status == STATUS_VOLUME_DISMOUNTED) {
                    return FLT_PREOP_SUCCESS_NO_CALLBACK;
                }
                else {
                    Data->IoStatus.Status = STATUS_ACCESS_DENIED;
                    Data->IoStatus.Information = 0;
                    return FLT_PREOP_COMPLETE;
                }
            }
            else {
                FltParseFileNameInformation(targetInfo);
                // 拦截逻辑
                if (FsRtlIsNameInExpression(&g_guardianRecoveryPath, &targetInfo->Name, TRUE, NULL) ||
                    FsRtlIsNameInExpression(&g_guardianPath, &targetInfo->Name, TRUE, NULL)) {
                    // 白名单进程直接放行
                    if (IsProcessTrusted()) {
                        FltReleaseFileNameInformation(targetInfo);
                        return FLT_PREOP_SUCCESS_NO_CALLBACK;
                    }
                    Data->IoStatus.Status = STATUS_ACCESS_DENIED;
                    Data->IoStatus.Information = 0;
                    FltReleaseFileNameInformation(targetInfo);
                    return FLT_PREOP_COMPLETE;
                }
                FltReleaseFileNameInformation(targetInfo);
            }
        }
    }

    // 通用拦截
    // 获取被操作目录
    PFLT_FILE_NAME_INFORMATION fileNameInfo = NULL;
    if (NT_SUCCESS(FltGetFileNameInformation(
        Data,
        FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT,
        &fileNameInfo
    ))) {

        NTSTATUS status = FltParseFileNameInformation(fileNameInfo);
        if (NT_SUCCESS(status)) {
            UNICODE_STRING saveFileNameInfo;
            WCHAR savefileNameInfo_buf[512];
            RtlInitEmptyUnicodeString(&saveFileNameInfo, savefileNameInfo_buf, 512 * sizeof(WCHAR));
            RtlCopyUnicodeString(&saveFileNameInfo, &fileNameInfo->Name);

            __try {
                // 拦截逻辑
                if (FsRtlIsNameInExpression(&g_guardianRecoveryPath, &saveFileNameInfo, TRUE, NULL) ||
                    FsRtlIsNameInExpression(&g_guardianPath, &saveFileNameInfo, TRUE, NULL)) {
                    // 白名单进程直接放行
                    if (IsProcessTrusted()) {
                        return FLT_PREOP_SUCCESS_NO_CALLBACK;
                    }
                    Data->IoStatus.Status = STATUS_ACCESS_DENIED;
                    Data->IoStatus.Information = 0;
                    FltReleaseFileNameInformation(fileNameInfo);
                    return FLT_PREOP_COMPLETE;
                }
            }
            __except (EXCEPTION_EXECUTE_HANDLER) {
                ;
            }
        }
        else {
            if (status == STATUS_FLT_DELETING_OBJECT || status == STATUS_VOLUME_DISMOUNTED) {
                FltReleaseFileNameInformation(fileNameInfo);
                return FLT_PREOP_SUCCESS_NO_CALLBACK;
            }
            Data->IoStatus.Status = STATUS_ACCESS_DENIED;
            Data->IoStatus.Information = 0;
            FltReleaseFileNameInformation(fileNameInfo);
            return FLT_PREOP_COMPLETE;
        }
        FltReleaseFileNameInformation(fileNameInfo);
    }
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

// 读取拦截策略----------------------------------------------------------
FLT_PREOP_CALLBACK_STATUS
CIGPreRead(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Out_ PVOID* CompletionContext
)
{
    *CompletionContext = NULL;
    UNREFERENCED_PARAMETER(FltObjects);

    // 快速核验
    // 高IRQL下直接放行
    if (KeGetCurrentIrql() > PASSIVE_LEVEL) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    // 获取被操作目录
    PFLT_FILE_NAME_INFORMATION fileNameInfo = NULL;
    if (NT_SUCCESS(FltGetFileNameInformation(
        Data,
        FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT,
        &fileNameInfo
    ))) {
        NTSTATUS status = FltParseFileNameInformation(fileNameInfo);
        if (NT_SUCCESS(status)) {
            UNICODE_STRING saveFileNameInfo;
            WCHAR savefileNameInfo_buf[512];
            RtlInitEmptyUnicodeString(&saveFileNameInfo, savefileNameInfo_buf, 512 * sizeof(WCHAR));
            RtlCopyUnicodeString(&saveFileNameInfo, &fileNameInfo->Name);

            // 拦截逻辑
            __try {
                if (FsRtlIsNameInExpression(&g_guardianRecoveryPath, &saveFileNameInfo, TRUE, NULL)) {
                    // 白名单进程直接放行
                    if (IsProcessTrusted()) {
                        return FLT_PREOP_SUCCESS_NO_CALLBACK;
                    }
                    Data->IoStatus.Status = STATUS_ACCESS_DENIED;
                    Data->IoStatus.Information = 0;
                    FltReleaseFileNameInformation(fileNameInfo);
                    return FLT_PREOP_COMPLETE;
                }
            }
            __except (EXCEPTION_EXECUTE_HANDLER) {
                    ;
                }
        }
        else {
            if (status == STATUS_FLT_DELETING_OBJECT || status == STATUS_VOLUME_DISMOUNTED) {
                FltReleaseFileNameInformation(fileNameInfo);
                return FLT_PREOP_SUCCESS_NO_CALLBACK;
            }
            Data->IoStatus.Status = STATUS_ACCESS_DENIED;
            Data->IoStatus.Information = 0;
            FltReleaseFileNameInformation(fileNameInfo);
            return FLT_PREOP_COMPLETE;
        }
        FltReleaseFileNameInformation(fileNameInfo);
    }
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}