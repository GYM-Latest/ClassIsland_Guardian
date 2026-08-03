using murrayju.ProcessExtensions;
using System.ServiceProcess;
using System.Threading;

namespace launcher
{
    public partial class launcher : ServiceBase
    {
        static void Main()
        {
            ServiceBase.Run(new launcher());
        }

        public launcher()
        {
            InitializeComponent();
        }

        protected override void OnStart(string[] args)
        {
            new Thread(Worker).Start();
        }

        protected override void OnStop()
        {
        }

        void Worker()
        {
            while (true)
            {
                // 等用户登录，拉 guardian
                while (true)
                {
                    try
                    {
                        string dir  = System.AppDomain.CurrentDomain.BaseDirectory;
                        string path = System.IO.Path.Combine(dir, "guardian.exe");
                        ProcessExtensions.StartProcessAsCurrentUser(path, visible: false);
                        break;
                    }
                    catch {
                        Thread.Sleep(5000);
                    }
                }
                Thread.Sleep(5000);
                // 盯着 guardian，退了就重新拉
                while (true)
                {
                    var procs = System.Diagnostics.Process.GetProcessesByName("guardian");
                    if (procs.Length == 0)
                    {
                        break;
                    }
                    Thread.Sleep(10000); 
                }
            }
        }
    }
}
