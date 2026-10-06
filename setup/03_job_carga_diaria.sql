/* =====================================================================================
   SETUP 03 (opcional) - Job de SQL Agent que ejecuta la carga diaria de tablones
   Requiere SQL Server Developer/Standard/Enterprise con SQL Agent iniciado (Express no tiene Agent).
   Ejecutar con un login sysadmin.

   Sirve para demostrar el ANÁLISIS DE IMPACTO: cuando un Pull Request modifica un objeto
   que este job invoca (por ejemplo tab.usp_CARGA_TB_CREDITO), el reporte del PR lo indica.
   ===================================================================================== */
USE [msdb];
GO

DECLARE @BASE SYSNAME;
DECLARE bases CURSOR LOCAL FAST_FORWARD FOR SELECT [name] FROM sys.databases WHERE [name] IN (N'BI_DEV', N'BI_PROD');
OPEN bases;
FETCH NEXT FROM bases INTO @BASE;
WHILE @@FETCH_STATUS = 0
BEGIN
    DECLARE @JOB SYSNAME = N'BI - Carga diaria tablones (' + @BASE + N')';

    IF EXISTS (SELECT 1 FROM dbo.sysjobs WHERE [name] = @JOB)
        EXEC dbo.sp_delete_job @job_name = @JOB;

    EXEC dbo.sp_add_job        @job_name = @JOB, @description = N'Carga tablones TB_CREDITO y TB_CRONOGRAMA del último fin de mes. Demo DataOps.';
    EXEC dbo.sp_add_jobstep    @job_name = @JOB, @step_name = N'Carga de tablones', @subsystem = N'TSQL',
                               @database_name = @BASE, @command = N'EXEC [ctl].[usp_CARGA_DIARIA];';
    EXEC dbo.sp_add_jobschedule @job_name = @JOB, @name = N'Diario 06:00', @freq_type = 4, @freq_interval = 1,
                               @active_start_time = 060000;
    EXEC dbo.sp_add_jobserver  @job_name = @JOB;

    FETCH NEXT FROM bases INTO @BASE;
END
CLOSE bases;
DEALLOCATE bases;
GO
