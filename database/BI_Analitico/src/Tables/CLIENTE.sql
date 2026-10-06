-- Fuente (simulada): maestro de clientes del core financiero. Datos ficticios.
CREATE TABLE [src].[CLIENTE]
(
    [ID_CLIENTE] INT NOT NULL,
    [TIPO_DOCUMENTO] CHAR(3) NOT NULL,
    [NRO_DOCUMENTO] VARCHAR(15) NOT NULL,
    [NOMBRE_COMPLETO] VARCHAR(150) NOT NULL,
    [FECHA_NACIMIENTO] DATE NULL,
    [SEXO] CHAR(1) NULL,
    [SEGMENTO] VARCHAR(30) NOT NULL,
    [FECHA_ALTA] DATE NOT NULL,
    CONSTRAINT [PK_CLIENTE] PRIMARY KEY CLUSTERED ([ID_CLIENTE])
);
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fuente (simulada): maestro de clientes del core financiero. Datos ficticios.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CLIENTE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Identificador interno del cliente.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CLIENTE',
    @level2type = N'COLUMN', @level2name = N'ID_CLIENTE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Tipo de documento de identidad (DNI, RUC, CE).',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CLIENTE',
    @level2type = N'COLUMN', @level2name = N'TIPO_DOCUMENTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Número de documento de identidad (ficticio).',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CLIENTE',
    @level2type = N'COLUMN', @level2name = N'NRO_DOCUMENTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Apellidos y nombres del cliente (ficticio).',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CLIENTE',
    @level2type = N'COLUMN', @level2name = N'NOMBRE_COMPLETO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha de nacimiento del cliente.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CLIENTE',
    @level2type = N'COLUMN', @level2name = N'FECHA_NACIMIENTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Sexo del cliente: M / F.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CLIENTE',
    @level2type = N'COLUMN', @level2name = N'SEXO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Segmento comercial del cliente (MICRO, PEQUENA, CONSUMO, PREFERENTE).',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CLIENTE',
    @level2type = N'COLUMN', @level2name = N'SEGMENTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha de alta del cliente en la entidad.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CLIENTE',
    @level2type = N'COLUMN', @level2name = N'FECHA_ALTA';
GO
