from django.db import models


class Roles(models.Model):
    idrol = models.AutoField(db_column='idRol', primary_key=True)
    nombrerol = models.CharField(db_column='NombreRol', max_length=45)
    descripcion = models.CharField(db_column='Descripción', max_length=100)

    class Meta:
        managed = False
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombrerol


class Usuarios(models.Model):
    idusuario = models.AutoField(db_column='idUsuario', primary_key=True)
    nombreusuario = models.CharField(db_column='NombreUsuario', max_length=45, unique=True)
    apellidopaterno = models.CharField(db_column='ApellidoPaterno', max_length=45)
    apellidomaterno = models.CharField(db_column='ApellidoMaterno', max_length=45)
    idrol = models.ForeignKey(
        'Roles', db_column='idRol', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='usuarios'
    )
    sexo = models.CharField(db_column='Sexo', max_length=45)
    password = models.CharField(db_column='Password', max_length=128)

    class Meta:
        managed = False
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.nombreusuario

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def nombre_completo(self):
        return f'{self.apellidopaterno} {self.apellidomaterno}'

    @property
    def rol_nombre(self):
        return self.idrol.nombrerol if self.idrol else None

    @property
    def rol_id(self):
        return self.idrol.idrol if self.idrol else None


class Anestesicos(models.Model):
    idanestesico = models.AutoField(db_column='idAnestesico', primary_key=True)
    nombreanestesico = models.CharField(db_column='NombreAnestesico', max_length=45)
    descripcion = models.CharField(db_column='Descripcion', max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'anestesicos'
        verbose_name = 'Anestésico'
        verbose_name_plural = 'Anestésicos'

    def __str__(self):
        return self.nombreanestesico


class Condiciones(models.Model):
    idcondicion = models.AutoField(db_column='idCondicion', primary_key=True)
    nombrecondicion = models.CharField(db_column='NombreCondicion', max_length=45)
    descripcion = models.CharField(db_column='Descripcion', max_length=250)

    class Meta:
        managed = False
        db_table = 'condiciones'
        verbose_name = 'Condición'
        verbose_name_plural = 'Condiciones'

    def __str__(self):
        return self.nombrecondicion


class Tejidos(models.Model):
    idtejido = models.AutoField(db_column='idTejido', primary_key=True)
    nombretejido = models.CharField(db_column='NombreTejido', max_length=45)
    descripcion = models.CharField(db_column='Descripcion', max_length=45)

    class Meta:
        managed = False
        db_table = 'tejidos'
        verbose_name = 'Tejido'
        verbose_name_plural = 'Tejidos'

    def __str__(self):
        return self.nombretejido


# ── Cajas se define ANTES de Ratas para que el FK directo funcione ──────────
class Cajas(models.Model):
    idcaja = models.AutoField(db_column='idCaja', primary_key=True)
    cantidadratas = models.IntegerField(db_column='CantidadRatas')
    sexo = models.CharField(db_column='Sexo', max_length=45)
    fechanacimiento = models.DateField(db_column='FechaNacimiento')
    idusuario = models.ForeignKey(
        Usuarios, db_column='idUsuario', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='cajas'
    )
    idubicacion = models.ForeignKey(          # ← nuevo
        'Ubicaciones', db_column='idUbicacion', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='cajas'
    )
    comentarios = models.CharField(db_column='Comentarios', max_length=45, blank=True, null=True)
    talla = models.CharField(db_column='Talla', max_length=45, blank=True, null=True)

    class Meta:
        managed  = False
        db_table = 'cajas'
        verbose_name        = 'Caja'
        verbose_name_plural = 'Cajas'

    def __str__(self):
        return f'Caja #{self.idcaja} ({self.sexo})'


class Ratas(models.Model):
    id = models.AutoField(primary_key=True)
    idrata = models.IntegerField(db_column='idRata')
    sexo = models.CharField(db_column='Sexo', max_length=10)
    idcaja = models.ForeignKey(
        Cajas, db_column='idCaja', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='ratas_en_caja'
    )
    fechacirugia = models.DateField(db_column='FechaCirugia', blank=True, null=True)
    numerocola = models.IntegerField(db_column='NumeroCola')
    idcondicion = models.ForeignKey(
        Condiciones, db_column='idCondicion', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='ratas'
    )

    class Meta:
        managed = False
        db_table = 'ratas'
        verbose_name = 'Rata'
        verbose_name_plural = 'Ratas'
        unique_together = [('idrata', 'sexo')]

    def __str__(self):
        prefix = self.sexo[0] if self.sexo else '?'
        return f'Rata {prefix}-{self.idrata} (cola: {self.numerocola})'

class Bitacora(models.Model):
    idbitacora = models.AutoField(db_column='idBitacora', primary_key=True)
    idrata = models.ForeignKey(
        Ratas, db_column='idRata', on_delete=models.CASCADE, related_name='bitacoras'
    )
    idusuario = models.ForeignKey(
        Usuarios, db_column='idUsuario', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='bitacoras'
    )
    fechacirujia = models.DateField(db_column='FechaCirujia')
    dosis = models.FloatField(db_column='Dosis', blank=True, null=True)
    dosistotal = models.FloatField(db_column='DosisTotal', blank=True, null=True)
    idanestesico = models.ForeignKey(
        Anestesicos, db_column='idAnestesico',
        on_delete=models.CASCADE, related_name='bitacoras'
    )
    pesoexperimento = models.FloatField(db_column='PesoExperimento', blank=True, null=True)
    actividad = models.TextField(db_column='Actividad', blank=True, null=True)
    idtejido = models.ForeignKey(
        Tejidos, db_column='idTejido', blank=True, null=True,
        on_delete=models.SET_NULL, related_name='bitacoras'
    )
    archivos = models.CharField(db_column='Archivos', max_length=45, blank=True, null=True)
    ubicacionarchivo = models.CharField(
        db_column='UbicacionArchivo', max_length=45, blank=True, null=True
    )
    notas = models.CharField(db_column='Notas', max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bitacora'
        verbose_name = 'Bitácora'
        verbose_name_plural = 'Bitácoras'

    def __str__(self):
        return f'Bitácora #{self.idbitacora} — Rata #{self.idrata_id}'


class PesoSemanal(models.Model):
    idrata   = models.ForeignKey(
        Ratas, db_column='idRata', on_delete=models.CASCADE,
        related_name='pesos'
    )
    fecha    = models.DateField(db_column='fecha')
    peso     = models.FloatField(db_column='peso')
    notas    = models.CharField(db_column='notas', max_length=100, blank=True, null=True)

    class Meta:
        managed  = False
        db_table = 'pesos_semanales'
        ordering = ['-fecha']
        verbose_name        = 'Peso semanal'
        verbose_name_plural = 'Pesos semanales'

    def __str__(self):
        return f'Rata #{self.idrata_id} — {self.fecha}: {self.peso}g'

class Ubicaciones(models.Model):
    idubicacion     = models.AutoField(db_column='idUbicacion', primary_key=True)
    nombreubicacion = models.CharField(db_column='NombreUbicacion', max_length=45)
    descripcion     = models.CharField(db_column='Descripcion', max_length=250, blank=True, null=True)
    class Meta:
        managed  = False
        db_table = 'ubicaciones'
        verbose_name        = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'

    def __str__(self):
        return self.nombreubicacion
