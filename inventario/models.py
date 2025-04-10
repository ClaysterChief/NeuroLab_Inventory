from django.db import models

class Anestesicos(models.Model):
    idanestesico = models.AutoField(db_column='idAnestesico', primary_key=True)
    nombreanestesico = models.CharField(db_column='NombreAnestesico', max_length=45)
    descripcion = models.CharField(db_column='Descripcion', max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'anestesicos'
        verbose_name = "Anestésico"
        verbose_name_plural = "Anestésicos"

class Bitacora(models.Model):
    idbitacora = models.AutoField(db_column='idBitacora', primary_key=True)
    idrata = models.ForeignKey('Ratas', db_column='idRata', on_delete=models.CASCADE)
    idusuario = models.ForeignKey('Usuarios', db_column='idUsuario', blank=True, null=True, on_delete=models.SET_NULL)
    fechacirujia = models.DateField(db_column='FechaCirujia')  # Nota: Hay un error tipográfico en "FechaCirujia". Debería ser "FechaCirugía".
    dosis = models.FloatField(db_column='Dosis', blank=True, null=True)
    dosistotal = models.FloatField(db_column='DosisTotal', blank=True, null=True)
    idanestesico = models.ForeignKey('Anestesicos', db_column='idAnestesico', on_delete=models.CASCADE)
    pesoexperimento = models.FloatField(db_column='PesoExperimento', blank=True, null=True)
    actividad = models.IntegerField(db_column='Actividad', blank=True, null=True)
    idtejido = models.ForeignKey('Tejidos', db_column='idTejido', blank=True, null=True, on_delete=models.SET_NULL)
    archivos = models.CharField(db_column='Archivos', max_length=45, blank=True, null=True)
    ubicacionarchivo = models.CharField(db_column='UbicacionArchivo', max_length=45)
    notas = models.CharField(db_column='Notas', max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bitacora'
        verbose_name = "Bitácora"
        verbose_name_plural = "Bitácoras"

class Cajas(models.Model):
    idcaja = models.AutoField(db_column='idCaja', primary_key=True)
    cantidadratas = models.IntegerField(db_column='CantidadRatas')
    idrata = models.ForeignKey('Ratas', db_column='idRata', on_delete=models.CASCADE)
    sexo = models.CharField(db_column='Sexo', max_length=45)
    fechanacimiento = models.DateField(db_column='FechaNacimiento')
    idusuario = models.ForeignKey('Usuarios', db_column='idUsuario', blank=True, null=True, on_delete=models.SET_NULL)
    comentarios = models.CharField(db_column='Comentarios', max_length=45)
    talla = models.CharField(db_column='Talla', max_length=45)

    class Meta:
        managed = False
        db_table = 'cajas'
        verbose_name = "Caja"
        verbose_name_plural = "Cajas"

class Condiciones(models.Model):
    idcondicion = models.AutoField(db_column='idCondicion', primary_key=True)
    nombrecondicion = models.CharField(db_column='NombreCondicion', max_length=45)
    descripcion = models.CharField(db_column='Descripcion', max_length=250)

    class Meta:
        managed = False
        db_table = 'condiciones'
        verbose_name = "Condición"
        verbose_name_plural = "Condiciones"

class Ratas(models.Model):
    idrata = models.OneToOneField(Bitacora, db_column='idRata', primary_key=True, on_delete=models.CASCADE)
    fechacirugia = models.DateField(db_column='FechaCirugia')
    pesosemanal = models.FloatField(db_column='PesoSemanal')
    numerocola = models.IntegerField(db_column='NumeroCola')
    idcondicion = models.ForeignKey(Condiciones, db_column='idCondicion', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'ratas'
        verbose_name = "Rata"
        verbose_name_plural = "Ratas"

class Roles(models.Model):
    idrol = models.AutoField(db_column='idRol', primary_key=True)
    nombrerol = models.CharField(db_column='NombreRol', max_length=45)
    descripcion = models.CharField(db_column='Descripción', max_length=45)

    class Meta:
        managed = False
        db_table = 'roles'
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

class Tejidos(models.Model):
    idtejido = models.AutoField(db_column='idTejido', primary_key=True)
    nombretejido = models.CharField(db_column='NombreTejido', max_length=45)
    descripcion = models.CharField(db_column='Descripcion', max_length=45)

    class Meta:
        managed = False
        db_table = 'tejidos'
        verbose_name = "Tejido"
        verbose_name_plural = "Tejidos"

class Usuarios(models.Model):
    idusuario = models.AutoField(db_column='idUsuario', primary_key=True)
    nombreusuario = models.CharField(db_column='NombreUsuario', max_length=45)
    apellidopaterno = models.CharField(db_column='ApellidoPaterno', max_length=45)
    apellidomaterno = models.CharField(db_column='ApellidoMaterno', max_length=45)
    idrol = models.ForeignKey(Roles, db_column='idRol', blank=True, null=True, on_delete=models.SET_NULL)
    sexo = models.CharField(db_column='Sexo', max_length=45)

    class Meta:
        managed = False
        db_table = 'usuarios'
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"