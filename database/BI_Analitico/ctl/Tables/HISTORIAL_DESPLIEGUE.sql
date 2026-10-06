-- Historial de despliegues realizados por el pipeline: qué versión del repositorio está instalada en la base.
CREATE TABLE [ctl].[HISTORIAL_DESPLIEGUE]
(
    [ID_DESPLIEGUE] INT IDENTITY(1,1) NOT NULL,
    [VERSION] VARCHAR(30) NOT NULL,
    [TIPO] VARCHAR(12) NOT NULL,
    [COMMIT_SHA] CHAR(40) NOT NULL,
    [RAMA] VARCHAR(100) NOT NULL,
    [PULL_REQUEST] INT NULL,
    [RIESGO] VARCHAR(12) NULL,
    [EJECUTADO_POR] VARCHAR(100) NOT NULL,
    [APROBADO_POR] VARCHAR(400) NULL,
    [MOTIVO] NVARCHAR(1000) NULL,
    [URL_EJECUCION] VARCHAR(400) NULL,
    [FECHA_DESPLIEGUE] DATETIME2(0) NOT NULL CONSTRAINT [DF_HISTORIAL_DESPLIEGUE_FECHA_DESPLIEGUE] DEFAULT (SYSDATETIME()),
    CONSTRAINT [PK_HISTORIAL_DESPLIEGUE] PRIMARY KEY CLUSTERED ([ID_DESPLIEGUE])
);
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Historial de despliegues realizados por el pipeline: qué versión del repositorio está instalada en la base.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Identificador del despliegue.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE',
    @level2type = N'COLUMN', @level2name = N'ID_DESPLIEGUE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Versión desplegada (tag o versión de desarrollo).',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE',
    @level2type = N'COLUMN', @level2name = N'VERSION';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Tipo de despliegue: DESPLIEGUE o ROLLBACK.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE',
    @level2type = N'COLUMN', @level2name = N'TIPO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Commit de Git desplegado.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE',
    @level2type = N'COLUMN', @level2name = N'COMMIT_SHA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Rama de origen.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE',
    @level2type = N'COLUMN', @level2name = N'RAMA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Número de Pull Request asociado.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE',
    @level2type = N'COLUMN', @level2name = N'PULL_REQUEST';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Clasificación de riesgo calculada por el pipeline.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE',
    @level2type = N'COLUMN', @level2name = N'RIESGO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Usuario de GitHub que originó la ejecución.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE',
    @level2type = N'COLUMN', @level2name = N'EJECUTADO_POR';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Usuarios que aprobaron el Pull Request.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE',
    @level2type = N'COLUMN', @level2name = N'APROBADO_POR';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Motivo (obligatorio en rollbacks).',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE',
    @level2type = N'COLUMN', @level2name = N'MOTIVO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Enlace a la ejecución del pipeline.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE',
    @level2type = N'COLUMN', @level2name = N'URL_EJECUCION';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha y hora del registro.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'HISTORIAL_DESPLIEGUE',
    @level2type = N'COLUMN', @level2name = N'FECHA_DESPLIEGUE';
GO
