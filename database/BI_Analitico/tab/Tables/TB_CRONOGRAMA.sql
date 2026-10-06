-- Tablón de cronogramas: una fila por cuota de cada crédito con saldo a la fecha de corte, con el estado de la cuota a esa fecha y atributos del crédito desnormalizados.
CREATE TABLE [tab].[TB_CRONOGRAMA]
(
    [FECHA_CORTE] DATE NOT NULL,
    [COD_CREDITO] VARCHAR(20) NOT NULL,
    [NRO_CUOTA] SMALLINT NOT NULL,
    [ID_CREDITO] INT NOT NULL,
    [NRO_DOCUMENTO] VARCHAR(15) NOT NULL,
    [NOMBRE_CLIENTE] VARCHAR(150) NOT NULL,
    [NOMBRE_AGENCIA] VARCHAR(80) NOT NULL,
    [NOMBRE_PRODUCTO] VARCHAR(80) NOT NULL,
    [MONEDA] CHAR(3) NOT NULL,
    [FECHA_VENCIMIENTO] DATE NOT NULL,
    [CAPITAL] DECIMAL(18,2) NOT NULL,
    [INTERES] DECIMAL(18,2) NOT NULL,
    [MONTO_CUOTA] DECIMAL(18,2) NOT NULL,
    [SALDO_CAPITAL_POST] DECIMAL(18,2) NOT NULL,
    [FECHA_PAGO] DATE NULL,
    [MONTO_PAGADO] DECIMAL(18,2) NULL,
    [ESTADO_CUOTA] VARCHAR(12) NOT NULL,
    [DIAS_ATRASO_CUOTA] INT NOT NULL,
    [FECHA_CARGA] DATETIME2(0) NOT NULL CONSTRAINT [DF_TB_CRONOGRAMA_FECHA_CARGA] DEFAULT (SYSDATETIME()),
    CONSTRAINT [PK_TB_CRONOGRAMA] PRIMARY KEY CLUSTERED ([FECHA_CORTE], [COD_CREDITO], [NRO_CUOTA])
);
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Tablón de cronogramas: una fila por cuota de cada crédito con saldo a la fecha de corte, con el estado de la cuota a esa fecha y atributos del crédito desnormalizados.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha de corte de la foto (fin de mes).',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'FECHA_CORTE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Código de negocio del crédito.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'COD_CREDITO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Número correlativo de la cuota.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'NRO_CUOTA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Identificador interno del crédito.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'ID_CREDITO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Número de documento del cliente.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'NRO_DOCUMENTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Apellidos y nombres del cliente.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'NOMBRE_CLIENTE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Agencia que originó el crédito.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'NOMBRE_AGENCIA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Producto de crédito.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'NOMBRE_PRODUCTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Moneda del crédito.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'MONEDA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha de vencimiento de la cuota.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'FECHA_VENCIMIENTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Amortización de capital de la cuota.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'CAPITAL';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Interés de la cuota.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'INTERES';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Monto total de la cuota (capital + interés).',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'MONTO_CUOTA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Saldo de capital del crédito luego de pagar esta cuota según cronograma.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'SALDO_CAPITAL_POST';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha de pago si se pagó hasta la fecha de corte; NULL en otro caso.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'FECHA_PAGO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Monto pagado hasta la fecha de corte; NULL si no se pagó.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'MONTO_PAGADO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Estado de la cuota a la fecha de corte: PAGADA, VENCIDA, POR_VENCER.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'ESTADO_CUOTA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Días de atraso de la cuota a la fecha de corte (0 si está pagada o por vencer).',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'DIAS_ATRASO_CUOTA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha y hora de carga del registro.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'TABLE', @level1name = N'TB_CRONOGRAMA',
    @level2type = N'COLUMN', @level2name = N'FECHA_CARGA';
GO
