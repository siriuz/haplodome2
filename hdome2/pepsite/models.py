import django.contrib.auth
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import utc
import os

NOW = models.DateTimeField(default=datetime.datetime.utcnow().replace(tzinfo=utc))


def fname():
    """docstring for fname"""
    pass


def yello():
    """docstring for yello"""
    pass


class Gene(models.Model):
    name = models.CharField(max_length=200)
    gene_class = models.IntegerField(null=True, blank=True)
    description = models.TextField(default='', blank=True)

    def __str__(self):
        return self.name + '|Class-' + str(self.gene_class)


class Allele(models.Model):
    gene = models.ForeignKey(Gene, null=True, blank=True)
    code = models.CharField(max_length=200)
    # dna_type = models.CharField(max_length=200)
    # ser_type = models.CharField(max_length=200)
    isSer = models.BooleanField(default=False)
    description = models.TextField(default='', blank=True, null=True)

    def get_summary(self):
        pass

    def get_class(self):
        return self.__class__

    def __str__(self):
        return self.code

    class Meta:
        unique_together = (('gene', 'code'),)

    def get_experiments(self):
        return Experiment.objects.filter(cell_line__alleles=self, antibody__alleles=self).distinct()


class Entity(models.Model):
    common_name = models.CharField(max_length=200)
    sci_name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(default='', blank=True, null=True)
    isOrganism = models.BooleanField(default=False)

    def __str__(self):
        return self.common_name

    def find_cell_lines(self):
        return CellLine.objects.filter(individuals__entity=self).distinct()


class Individual(models.Model):
    identifier = models.CharField(max_length=200, unique=True)
    description = models.TextField(default='', blank=True, null=True)
    nation_origin = models.CharField(max_length=200, blank=True, null=True)
    entity = models.ForeignKey(Entity, blank=True, null=True)
    isHost = models.BooleanField(default=False)
    isAnonymous = models.BooleanField(default=True)
    web_ref = models.CharField(max_length=200, default='', null=True, blank=True)

    def __str__(self):
        return self.identifier


class CellLine(models.Model):
    name = models.CharField(max_length=200)
    tissue_type = models.CharField(max_length=200, blank=True, null=True)
    isTissue = models.BooleanField(default=False)
    description = models.TextField(default='', blank=True, null=True)
    # host = models.ForeignKey( Organism, related_name = 'HostCell' )
    # infecteds = models.ManyToManyField( Organism, related_name = 'Infections' )
    individuals = models.ManyToManyField(Individual)
    alleles = models.ManyToManyField(Allele, through='Expression')
    parent = models.ForeignKey('self', null=True, blank=True)

    # antibodies = models.ManyToManyField( Antibody )

    class Meta:
        """docstring for Meta"""
        # unique_together = ('name', 'description')

    def __str__(self):
        return self.name

    def get_antibodies_targeting(self):
        return Antibody.objects.filter(alleles__cellline=self, experiments__cell_line=self).distinct()

    def get_antibodies(self):
        return Antibody.objects.filter(experiments__cell_line=self).distinct()

    def get_experiments(self):
        return Experiment.objects.filter(cell_line=self).distinct()

    def get_organisms(self):
        return Entity.objects.filter(isOrganism=True, individual__cellline=self)


class Expression(models.Model):
    """docstring for Expression"""
    cell_line = models.ForeignKey(CellLine)
    allele = models.ForeignKey(Allele)
    isSilenced = models.BooleanField(default=False)
    expression_level = models.FloatField(default=100.0)

    def __str__(self):
        """docstring for __str__"""
        return self.cell_line.name + '|' + self.allele.code


class Lodgement(models.Model):
    """docstring for Lodgement"""
    datetime = models.DateTimeField()
    title = models.CharField(max_length=300, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    datafilename = models.CharField(max_length=400, blank=True, null=True)
    isFree = models.BooleanField(default=False)

    def __str__(self):
        return self.datetime.strftime("%Y-%m-%d %H:%M:%S")

    def filename(self):
        return os.path.basename(self.datafile.name)

    class Meta:
        permissions = (
            ('view_lodgement', 'can view lodgement'),
            ('edit_lodgement', 'can edit lodgement'),
        )

    def get_experiment(self):
        try:
            return Experiment.objects.filter(dataset__lodgement=self).distinct()[0]
        except:
            return None


class Experiment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(default='', blank=True, null=True)
    # date_time = models.DateTimeField('date run')
    # data = models.FileField()
    cell_line = models.ForeignKey(CellLine)
    # lodgement = models.ForeignKey( Lodgement )
    notes = models.TextField(default='', blank=True, null=True)

    # morenotes = models.TextField( default = '',blank=True, null=True )
    # proteins = models.ManyToManyField( 'Protein', blank=True, null=True )

    class Meta:
        permissions = (
            ('view_experiment', 'can view experiment'),
            ('view_experiment_disallowed', 'can view all experiment entries'),
            ('edit_experiment', 'can edit experiment'),
        )

    def __str__(self):
        return self.title

    def get_common_alleles(self):
        return Allele.objects.filter(antibody__experiments=self, cellline__experiment=self)

    def get_proteins(self):
        """docstring for get_proteins"""
        return Protein.objects.filter(peptide__ion__experiments=self)

    def get_publications(self):
        """docstring for get_publications"""
        return list(set(Publication.objects.filter(lodgements__dataset__experiment=self)))

    @property
    def publications(self):
        """docstring for get_publications"""
        return list(set(Publication.objects.filter(lodgements__dataset__experiment=self)))

    def get_lodgements(self):
        return Lodgement.objects.filter(dataset__experiment__id=self.id).distinct().order_by('datafilename')


class Antibody(models.Model):
    name = models.CharField(max_length=200, unique=True)
    link = models.CharField(max_length=400, blank=True, null=True)
    description = models.TextField(default='', blank=True, null=True)
    alleles = models.ManyToManyField(Allele, blank=True, null=True)
    experiments = models.ManyToManyField(Experiment, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_cell_lines_targeted(self):
        return CellLine.objects.filter(alleles__antibody=self, experiment__antibody=self).distinct()


class Ptm(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(default='', blank=True, null=True)
    mass_change = models.FloatField(null=True, blank=True)

    def fname(self):
        """docstring for fname"""
        pass

    def __str__(self):
        return self.description + '|' + str(self.mass_change)


class Protein(models.Model):
    prot_id = models.CharField(max_length=200, blank=True, null=True)
    name = models.TextField(default='', blank=True, null=True)  # CharField(max_length=200)
    description = models.TextField(default='', blank=True, null=True)
    sequence = models.TextField(default='', blank=True, null=True)

    def get_uniprot_link(self):
        """docstring for get_uniprot_code"""
        externaldb = ExternalDb.objects.get(db_name='UniProt')
        return externaldb.url_stump + self.prot_id + externaldb.url_suffix

    def get_uniprot_code(self):
        """docstring for get_uniprot_code"""
        lu = LookupCode.objects.get(protein=self, externaldb__db_name='UniProt')
        return lu.code

    def __str__(self):
        return self.description

    def get_experiments(self):
        return Experiment.objects.filter(ion__peptides__proteins=self).distinct()


class Peptide(models.Model):
    sequence = models.CharField(max_length=200)
    mass = models.FloatField(null=True, blank=True)

    # ptms = models.ManyToManyField( Ptm )

    def __str__(self):
        return self.sequence

    def get_ptms(self):
        """docstring for get_ptms"""
        return Ptm.objects.filter(idestimate__peptide=self).distinct()

    def get_proteins(self):
        """docstring for get_ptms"""
        return Protein.objects.filter(peptoprot__peptide=self).distinct()


class Position(models.Model):
    """docstring for Position"""
    initial_res = models.IntegerField()
    final_res = models.IntegerField()

    def __str__(self):
        """docstring for __str__"""
        return "%d-%d" % (self.initial_res, self.final_res)


class Ion(models.Model):
    precursor_mass = models.FloatField()
    mz = models.FloatField()
    charge_state = models.IntegerField()
    retention_time = models.FloatField()
    experiment = models.ForeignKey(Experiment)
    spectrum = models.CharField(default='', max_length=200, blank=True, null=True)
    dataset = models.ForeignKey('Dataset')
    peptides = models.ManyToManyField(Peptide, through='IdEstimate')

    # antibodies = models.ManyToManyField( Antibody )
    # cell_lines = models.ManyToManyField( CellLine )

    def __str__(self):
        return str(self.precursor_mass) + '|' + str(self.charge_state) + '|' + str(self.mz)


class IdEstimate(models.Model):
    peptide = models.ForeignKey(Peptide)
    ion = models.ForeignKey(Ion)
    ptms = models.ManyToManyField(Ptm)
    proteins = models.ManyToManyField(Protein)
    # experiment = models.ForeignKey(Experiment)
    delta_mass = models.FloatField()
    confidence = models.FloatField()
    isValid = models.BooleanField(default=False)
    # isRedundent = models.BooleanField( default = False )
    isRemoved = models.BooleanField(default=False)
    reason = models.TextField(default='', blank=True, null=True)

    def check_ptm(self):
        """docstring for check_ptm"""
        if not self.ptm or self.ptm.description in ('', ' ',
                                                    '[undefined]', '[undefined] '):
            return False
        else:
            return True

    def __str__(self):
        return str(self.delta_mass) + '|' + str(self.confidence)

    def get_lodgement(self):
        """docstring for get_lodgement"""
        return Lodgement.objects.get(dataset__ions__idestimate=self)

    def get_dataset(self):
        """docstring for get_lodgement"""
        return Dataset.objects.get(ions__idestimate=self)


class Manufacturer(models.Model):
    """docstring for Manufacturer"""
    name = models.CharField(max_length=200)

    def __str__(self):
        """docstring for __str__"""
        return self.name


class Instrument(models.Model):
    """docstring for Instrument"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, blank=True, null=True)

    def __unicode__(self):
        """docstring for __str__"""
        return self.name


class Dataset(models.Model):
    """docstring for Dataset"""
    title = models.CharField(max_length=300, unique=True)
    rank = models.IntegerField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    data = models.FileField(blank=True, null=True)
    gradient_min = models.FloatField(null=True, blank=True)
    gradient_max = models.FloatField(null=True, blank=True)
    gradient_duration = models.FloatField(null=True, blank=True)
    instrument = models.ForeignKey(Instrument)
    lodgement = models.ForeignKey(Lodgement)
    experiment = models.ForeignKey(Experiment)
    notes = models.TextField(default='', blank=True, null=True)
    confidence_cutoff = models.FloatField(null=True, blank=True)
    dmass_cutoff = models.FloatField(null=True, blank=True)

    class Meta:
        permissions = (
            ('view_dataset', 'can view dataset'),
            ('edit_dataset', 'can edit dataset'),
        )

    def __str__(self):
        """docstring for __str__"""
        return self.title

    def update_rank(self):
        """docstring for update_rank"""
        expt = Experiment.objects.get(dataset=self)
        curmax = max([b.rank for b in expt.dataset_set.all()])
        # print curmax
        # if self.rank is not None:
        if curmax is not None:
            if self.rank is None:
                self.rank = curmax + 1
        else:
            self.rank = 0
        self.save()


class ExternalDb(models.Model):
    """docstring for ExternalDb"""
    db_name = models.CharField(max_length=200)
    url_stump = models.CharField(max_length=400)
    url_suffix = models.CharField(max_length=400, blank=True, null=True)

    def __str__(self):
        """docstring for __str__"""
        return self.db_name + '|' + self.url_stump


class LookupCode(models.Model):
    """docstring for Code"""
    code = models.CharField(max_length=200)
    externaldb = models.ForeignKey(ExternalDb)
    protein = models.ForeignKey(Protein, null=True, blank=True)
    cell_lines = models.ManyToManyField(CellLine)

    def __str__(self):
        """docstring for __str__"""
        return self.code + '|' + self.externaldb.db_name


class Publication(models.Model):
    """docstring for Publication"""
    title = models.TextField(blank=True, null=True)
    journal = models.TextField(blank=True, null=True)
    display = models.TextField(default='', blank=True, null=True)
    lodgements = models.ManyToManyField(Lodgement)
    cell_lines = models.ManyToManyField(CellLine)
    lookupcode = models.OneToOneField(LookupCode, null=True, blank=True)

    def __unicode__(self):
        """docstring for _"""
        return self.title + '|' + self.journal

    def refresh_display(self):
        """docstring for refresh_display
        idea is to get authors etc from PubMed and condense into string"""
        pass
