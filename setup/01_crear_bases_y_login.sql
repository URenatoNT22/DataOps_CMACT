/* =====================================================================================
   SETUP 01 - Bases de datos de la demo y cuenta de servicio del pipeline
   Ejecutar UNA sola vez, en SSMS / Azure Data Studio, con un login sysadmin.

   Qué hace:
     1. Crea las bases BI_DEV y BI_PROD (vacías: el esquema lo crea el pipeline).
     2. Crea el login svc_pipeline: la ÚNICA identidad que despliega cambios.
        - db_owner solo en BI_DEV y BI_PROD (nunca sysadmin, nunca 'sa').
        - Lectura de jobs de SQL Agent en msdb (para el análisis de impacto).
     3. NO otorga permisos a personas: los analistas no hacen DDL directo.

   ANTES DE EJECUTAR: cambia la contraseña de abajo por una fuerte y guárdala solo en
   GitHub > Settings > Secrets and variables > Actions > SQL_PASSWORD.
   ===================================================================================== */
USE [master];
GO

DECLARE @PASSWORD NVARCHAR(128) = N'CAMBIAR_por_una_clave_fuerte_#2026';   -- <== CAMBIAR

IF DB_ID(N'BI_DEV') IS NULL
    CREATE DATABASE [BI_DEV];
IF DB_ID(N'BI_PROD') IS NULL
    CREATE DATABASE [BI_PROD];

IF SUSER_ID(N'svc_pipeline') IS NULL
BEGIN
    DECLARE @sql NVARCHAR(MAX) = N'CREATE LOGIN [svc_pipeline] WITH PASSWORD = ' + QUOTENAME(@PASSWORD, '''')
                               + N', CHECK_POLICY = ON, CHECK_EXPIRATION = OFF, DEFAULT_DATABASE = [BI_DEV];';
    EXEC (@sql);
END
GO

ALTER DATABASE [BI_DEV]  SET RECOVERY SIMPLE;
ALTER DATABASE [BI_PROD] SET RECOVERY SIMPLE;
GO

USE [BI_DEV];
GO
IF USER_ID(N'svc_pipeline') IS NULL CREATE USER [svc_pipeline] FOR LOGIN [svc_pipeline];
ALTER ROLE [db_owner] ADD MEMBER [svc_pipeline];
GO

USE [BI_PROD];
GO
IF USER_ID(N'svc_pipeline') IS NULL CREATE USER [svc_pipeline] FOR LOGIN [svc_pipeline];
ALTER ROLE [db_owner] ADD MEMBER [svc_pipeline];
GO

-- Lectura de jobs de SQL Agent (análisis de impacto: qué jobs llaman a los objetos modificados)
USE [msdb];
GO
IF USER_ID(N'svc_pipeline') IS NULL CREATE USER [svc_pipeline] FOR LOGIN [svc_pipeline];
ALTER ROLE [SQLAgentReaderRole] ADD MEMBER [svc_pipeline];
GRANT SELECT ON [dbo].[sysjobs]     TO [svc_pipeline];
GRANT SELECT ON [dbo].[sysjobsteps] TO [svc_pipeline];
GO

PRINT N'Listo: BI_DEV, BI_PROD y svc_pipeline creados.';
PRINT N'Siguiente paso: configurar los secretos en GitHub y ejecutar el workflow "Despliegue" (ver docs/03_INSTALACION.md).';
GO
