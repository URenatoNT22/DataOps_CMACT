-- Fuente (simulada): catálogo de agencias. Datos ficticios.
CREATE TABLE [src].[AGENCIA]
(
    [ID_AGENCIA] SMALLINT NOT NULL,
    [NOMBRE_AGENCIA] VARCHAR(80) NOT NULL,
    [REGION] VARCHAR(50) NOT NULL,
    [ZONA] VARCHAR(50) NOT NULL,
    CONSTRAINT [PK_AGENCIA] PRIMARY KEY CLUSTERED ([ID_AGENCIA])
);
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fuente (simulada): catálogo de agencias. Datos ficticios.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'AGENCIA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Identificador de la agencia.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'AGENCIA',
    @level2type = N'COLUMN', @level2name = N'ID_AGENCIA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Nombre de la agencia.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'AGENCIA',
    @level2type = N'COLUMN', @level2name = N'NOMBRE_AGENCIA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Región geográfica de la agencia.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'AGENCIA',
    @level2type = N'COLUMN', @level2name = N'REGION';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Zona comercial a la que pertenece la agencia.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'AGENCIA',
    @level2type = N'COLUMN', @level2name = N'ZONA';
GO
