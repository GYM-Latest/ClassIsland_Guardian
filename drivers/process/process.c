#include <ntifs.h>

PVOID g_RegHandle = NULL;

#pragma data_seg("NONPAGED")
// 定义白名单路径
UNICODE_STRING g_guardianExePath = { 0 };
UNICODE_STRING g_configExePath = { 0 };
// 定义保护进程名
UNICODE_STRING g_guardianExeName = { 0 };
UNICODE_STRING g_classislandExeName = { 0 };
#pragma data_seg()

OB_PREOP_CALLBACK_STATUS CIGProcessPreOperation(
    _In_ PVOID RegistrationContext,
    _In_ POB_PRE_OPERATION_INFORMATION OperationInformation
);

NTSTATUS DriverEntry(
	_In_ PDRIVER_OBJECT DriverObject,
	_In_ PUNICODE_STRING RegistryPath
);

NTSTATUS
CIGProcessUnload(
	_In_ PDRIVER_OBJECT DriverObject
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

    // guardianExeName
    buffer = (PWCHAR)ExAllocatePool2(POOL_FLAG_NON_PAGED,
        sizeof(L"guardian.exe"),
        'CIGP');
    if (buffer) {
        RtlCopyMemory(buffer, L"guardian.exe",
            sizeof(L"guardian.exe"));
        g_guardianExeName.Buffer = buffer;
        g_guardianExeName.Length = (USHORT)(sizeof(L"guardian.exe") - sizeof(WCHAR));
        g_guardianExeName.MaximumLength = (USHORT)sizeof(L"guardian.exe");
    }

    // classislandExeName
    buffer = (PWCHAR)ExAllocatePool2(POOL_FLAG_NON_PAGED,
        sizeof(L"ClassIsland.Desktop.exe"),
        'CIGP');
    if (buffer) {
        RtlCopyMemory(buffer, L"ClassIsland.Desktop.exe",
            sizeof(L"ClassIsland.Desktop.exe"));
        g_classislandExeName.Buffer = buffer;
        g_classislandExeName.Length = (USHORT)(sizeof(L"ClassIsland.Desktop.exe") - sizeof(WCHAR));
        g_classislandExeName.MaximumLength = (USHORT)sizeof(L"ClassIsland.Desktop.exe");
    }

    // 配置 OB_OPERATION_REGISTRATION
    OB_OPERATION_REGISTRATION opReg = { 0 };
    opReg.ObjectType = PsProcessType;
    opReg.Operations = OB_OPERATION_HANDLE_CREATE |
        OB_OPERATION_HANDLE_DUPLICATE;
    opReg.PreOperation = CIGProcessPreOperation;
    opReg.PostOperation = NULL;

    // 配置 OB_CALLBACK_REGISTRATION
    UNICODE_STRING altitude;
    RtlInitUnicodeString(&altitude, L"328000.1");

    OB_CALLBACK_REGISTRATION cbReg = { 0 };
    cbReg.Version = OB_FLT_REGISTRATION_VERSION;
    cbReg.OperationRegistrationCount = 1;
    cbReg.Altitude = altitude;
    cbReg.RegistrationContext = NULL;
    cbReg.OperationRegistration = &opReg;

    // 注册 ObRegisterCallbacks
    status = ObRegisterCallbacks(&cbReg, &g_RegHandle);
    if (!NT_SUCCESS(status)) {
        return status;
    }

	DriverObject->DriverUnload = CIGProcessUnload;
    return STATUS_SUCCESS;
}

NTSTATUS
CIGProcessUnload(
	_In_ PDRIVER_OBJECT DriverObject
)
{
    UNREFERENCED_PARAMETER(DriverObject);

    // 卸载进程回调
    if (g_RegHandle) {
        ObUnRegisterCallbacks(g_RegHandle);
        g_RegHandle = NULL;
    }

    // 释放占用的内存
    if (g_guardianExePath.Buffer)       ExFreePool(g_guardianExePath.Buffer);
    if (g_configExePath.Buffer)         ExFreePool(g_configExePath.Buffer);
    if (g_guardianExeName.Buffer)       ExFreePool(g_guardianExeName.Buffer);
    if (g_classislandExeName.Buffer)    ExFreePool(g_classislandExeName.Buffer);

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
OB_PREOP_CALLBACK_STATUS CIGProcessPreOperation(
    _In_ PVOID RegistrationContext,
    _In_ POB_PRE_OPERATION_INFORMATION OperationInformation
) {
    UNREFERENCED_PARAMETER(RegistrationContext);
    // 快速核验
    // 请求来自内核直接放行
    if (OperationInformation->KernelHandle == 1) {
        return OB_PREOP_SUCCESS;
    }
    // 高IRQL下直接放行
    if (KeGetCurrentIrql() > PASSIVE_LEVEL) {
        return OB_PREOP_SUCCESS;
    }
    // 线程操作直接放行（虽然不可能但是这里还是检查一下）
    if (OperationInformation->ObjectType != *PsProcessType) {
        return OB_PREOP_SUCCESS;
    }

    // 通用拦截
    PEPROCESS targetProcess = (PEPROCESS)OperationInformation->Object;
    PUNICODE_STRING processPath = NULL;
    if (NT_SUCCESS(SeLocateProcessImageName(targetProcess, &processPath)) && processPath != NULL) {
        PWCHAR saveProcessPath = (PWCHAR)ExAllocatePool2(
            POOL_FLAG_NON_PAGED,
            processPath->Length + sizeof(WCHAR),
            'CIGP'
        );
        if (saveProcessPath != NULL) {
            RtlCopyMemory(saveProcessPath, processPath->Buffer, processPath->Length);
            saveProcessPath[processPath->Length / sizeof(WCHAR)] = L'\0';
            if (wcsstr(saveProcessPath, g_guardianExeName.Buffer) != NULL ||
                wcsstr(saveProcessPath, g_classislandExeName.Buffer) != NULL) {
                // 白名单进程直接放行
                if (IsProcessTrusted()) {
                    return OB_PREOP_SUCCESS;
                }
                PACCESS_MASK DesiredAccess = NULL;
                switch (OperationInformation->Operation) {
                case OB_OPERATION_HANDLE_CREATE:
                    DesiredAccess = &OperationInformation->Parameters->CreateHandleInformation.DesiredAccess;
                    break;
                case OB_OPERATION_HANDLE_DUPLICATE:
                    DesiredAccess = &OperationInformation->Parameters->DuplicateHandleInformation.DesiredAccess;
                    break;
                }
                if (DesiredAccess) {
                    *DesiredAccess &= ~(0x0001);  // PROCESS_TERMINATE
                }
            }
            ExFreePoolWithTag(saveProcessPath, 'CIGP');
        }
        ExFreePool(processPath);
    }
    return OB_PREOP_SUCCESS;
}