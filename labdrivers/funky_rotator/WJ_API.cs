/*
C#接口文件
*/
using System;
using System.Text;
using System.Runtime.InteropServices;
public class WJ_API
{

//通信初始化指令
[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Open(Int32 num_scom);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Close();

//查询指令
[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Get_Axis_Acc(Int32 AxisNUM, ref Int32 pValue);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Get_Axis_Dec(Int32 AxisNUM, ref Int32 pValue);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Get_Axis_Vel(Int32 AxisNUM, ref Int32 pValue);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Get_Axis_Subdivision(Int32 AxisNUM, ref Int32 pValue);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Get_Axis_Status(Int32 AxisNUM, ref Int32 pValue);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Get_Axes_Status(Int32[] pValue);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Get_Axis_Pulses(Int32 AxisNUM, ref Int32 pValue);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Get_Axes_Pulses(Int32[] pValue);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Get_Axes_Num(ref Int32 pValue);


//运动指令
[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Move_Axis_Pulses(Int32 AxisNUM, Int32 Value);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Move_Axes_Pulses(Int32[] pValue);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Move_Axis_Vel(Int32 AxisNUM, Int32 Value);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Move_Axes_Vel(Int32[] pValue);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Move_Axis_Emergency_Stop(Int32 AxisNUM);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Move_Axis_Slow_Stop(Int32 AxisNUM);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Move_Axis_Home(Int32 AxisNUM, Int32 Value);

//设置指令
[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Set_Axis_Acc(Int32 AxisNUM, Int32 Value);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Set_Axis_Dec(Int32 AxisNUM, Int32 Value);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Set_Axis_Vel(Int32 AxisNUM, Int32 Value);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Set_Axis_Subdivision(Int32 AxisNUM, Int32 Value);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Set_Axis_Slow_Stop(Int32 AxisNUM, Int32 Value);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Set_Led_Twinkle();

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Set_Axis_Pulses_Zero(Int32 AxisNUM);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Set_Default();

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Set_Move_Axis_Vel_Acc(Int32 AxisNUM, Int32 Value);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_Set_Axis_Home_Pulses(Int32 AxisNUM, Int32 Value);

//IO指令
[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_IO_Output(Int32 IONUM, Int32 Value);

[DllImport("WJ_API.dll",CharSet=CharSet.Ansi,CallingConvention=CallingConvention.StdCall)]
public static extern Int32 WJ_IO_Input(Int32 IONUM, ref Int32 pValue);

}

