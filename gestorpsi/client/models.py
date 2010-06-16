# -*- coding: utf-8 -*-

"""
Copyright (C) 2008 GestorPsi

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import reversion
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from gestorpsi.person.models import Person
from gestorpsi.util.uuid_field import UuidField

CLIENT_STATUS = ( ('0','Inativo'),('1','Ativo'))

FAMILY_RELATION = ( 
    (1, _('Parents')),
    (2, _('Children')),
    (3, _('Siblings')),
    (4, _('Step parents')),
    (5, _('Stepchildren')),
    (6, _('Half sibling or stepsibling')),
    (7, _('Uncles')),
    (8, _('Nephews')),
    (9, _('Cousins')),
    (10, _('Grandparents')),
    (11, _('Grandchildren')),
    (12, _('Spouse')),
    (13, _('Others')),
)

FAMILY_RELATION_REVERSE = ( 
    (1, _('Children')),
    (2, _('Parents')),
    (3, _('Siblings')),
    (4, _('Stepchildren')),
    (5, _('Step parents')),
    (6, _('Half sibling or stepsibling')),
    (7, _('Nephews')),
    (8, _('Uncles')),
    (9, _('Cousins')),
    (10, _('Grandchildren')),
    (11, _('Grandparents')),
    (12, _('Spouse')),
    (13, _('Others')),
)


class MaritalStatus(models.Model):
    description = models.CharField(max_length=20)
    def __unicode__(self):
        return u"%s" % self.description
    class Meta:
        ordering = ['description']

class Family(models.Model):
    client = models.ForeignKey('Client', related_name='family_client_selected', null=True, blank=True)
    client_related = models.ForeignKey('Client', related_name='family_client_related', null=True, blank=True)
    relation_level = models.IntegerField(choices = FAMILY_RELATION, max_length=2, null=True, blank=True)
    responsible = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s" % self.get_relation_level_display()

''' class not in use! moved to parents relations to class Family. removing soon  ''' 
class Relation(models.Model):
    description = models.CharField(max_length=30)
    def __unicode__(self):
        return u"%s" % self.description
    class Meta:
        ordering = ['description']

''' class not in use! moved to parents relations to class Family. removing soon ''' 
class PersonLink(models.Model):
    id = UuidField(primary_key=True)
    person = models.OneToOneField(Person)
    relation = models.ForeignKey(Relation)
    responsible = models.BooleanField(default=False)
    def __unicode__(self):
        return u"%s" % self.person.name

class ClientManager(models.Manager):
    def active(self, organization):
        return super(Client, self).get_query_set().filter(active=True, person__organization = organization).order_by('person__name')
    
    def deactive(self, organization):
        return super(Client, self).get_query_set().filter(active=False, person__organization = organization).order_by('person__name')
    
    def from_organization(self, organization, query_pk_in=None):
        
        """
        return clients list from logged organization
        and/or with a pk range filter
        ...
        actually used in report app
        """
        
        query = super(ClientManager, self).get_query_set().filter(person__organization = organization)

        if query_pk_in:
            query = query.filter(pk__in=[ i.client.id for i in query_pk_in])
        query = query.order_by('person__name')

        return query

    def from_user(self, user, status=None, query_pk_in=None):

        object_list = Client.objects.from_organization(user.get_profile().org_active, query_pk_in)
        
        if status:
            if status == 'deactive' : status = '0'
            else:  status = '1'
            object_list = object_list.filter(clientStatus = status)
        
        if not user.groups.filter(name='administrator') and not user.groups.filter(name='secretary'):
            added_by_me = [] # registers added by me, got by django-reversion
            for c in Client.objects.all():
                if c.revision().user == user:
                    added_by_me.append(c.id)

            object_list = object_list.filter(Q(referral__professional = user.profile.person.careprofessional.id) \
                            | Q(pk__in=added_by_me) \
                            | Q(referral__service__responsibles=user.profile.person.careprofessional) \
                            ).distinct().order_by('person__name')
        
        return object_list

    def Individuals(self, organization, query_pk_in=None):
        q = super(ClientManager, self).get_query_set().filter(person__active=True, person__company__isnull=True, person__organization=organization)
        if query_pk_in:
            q = q.filter(pk__in=query_pk_in)
        return q

    def Companies(self, organization, query_pk_in=None):
        q = super(ClientManager, self).get_query_set().filter(person__active=True, person__company__isnull=False, person__organization=organization)
        if query_pk_in:
            q = q.filter(pk__in=query_pk_in)
        return q

    def GenderMale(self, organization, query_pk_in=None):
        q = super(ClientManager, self).get_query_set().filter(person__active=True, person__gender='1', person__organization=organization)
        if query_pk_in:
            q = q.filter(pk__in=query_pk_in)
        return q
    
    def GenderFemale(self, organization, query_pk_in=None):
        q = super(ClientManager, self).get_query_set().filter(person__active=True, person__gender='2', person__organization=organization)
        if query_pk_in:
            q = q.filter(pk__in=query_pk_in)
        return q

    def GenderUnknown(self, organization, query_pk_in=None):
        q = super(ClientManager, self).get_query_set().filter(person__active=True, person__organization=organization).exclude(person__gender='1').exclude(person__gender='2')
        if query_pk_in:
            q = q.filter(pk__in=query_pk_in)
        return q

    def AgeChildren(self, organization, query_pk_in=None):
        q = super(ClientManager, self).get_query_set().filter(person__active=True, person__birthDate__gt = datetime.now()-relativedelta(years=13), person__organization=organization)
        if query_pk_in:
            q = q.filter(pk__in=query_pk_in)
        return q

    def AgeTeen(self, organization, query_pk_in=None):
        q = super(ClientManager, self).get_query_set().filter(person__active=True, person__birthDate__lte = datetime.now()-relativedelta(years=13), person__birthDate__gt = datetime.now()-relativedelta(years=18), person__organization=organization)
        if query_pk_in:
            q = q.filter(pk__in=query_pk_in)
        return q

    def AgeAdult(self, organization, query_pk_in=None):
        q = super(ClientManager, self).get_query_set().filter(person__active=True, person__birthDate__lte = datetime.now()-relativedelta(years=18), person__birthDate__gt = datetime.now()-relativedelta(years=66), person__organization=organization)
        if query_pk_in:
            q = q.filter(pk__in=query_pk_in)
        return q

    def AgeElderly(self, organization, query_pk_in=None):
        q = super(ClientManager, self).get_query_set().filter(person__active=True, person__birthDate__lte = datetime.now()-relativedelta(years=66), person__organization=organization)
        if query_pk_in:
            q = q.filter(pk__in=query_pk_in)
        return q

    def AgeUnknown(self, organization, query_pk_in=None):
        q = super(ClientManager, self).get_query_set().filter(person__active=True, person__birthDate__isnull=True, person__organization=organization)
        if query_pk_in:
            q = q.filter(pk__in=query_pk_in)
        return q

class Client(models.Model):
    id = UuidField(primary_key=True)
    person = models.OneToOneField(Person)
    idRecord = models.PositiveIntegerField()
    legacyRecord = models.CharField(max_length=15)
    admission_date = models.DateField(null=True)
    clientStatus = models.CharField(max_length=1, default='1', choices=CLIENT_STATUS)
    comments = models.TextField(blank=True)
    objects = ClientManager()

    def __unicode__(self):
        return (u"%s" % (self.person.name, )) if self.person.is_company() else (u"%s" % (self.person.name))
    
    class Meta:
        ordering = ['person']

    def revision(self):
        return reversion.models.Version.objects.get_for_object(self).order_by('-revision__date_created').latest('revision__date_created').revision

    def revision_created(self):
        return reversion.models.Version.objects.get_for_object(self).order_by('revision__date_created').latest('revision__date_created').revision

    def referrals_charged(self):
        return self.referral_set.charged().filter(client=self)

    def referrals_discharged(self):
        return self.referral_set.discharged().filter(client=self)
    
    def family_members(self):
        family_list = []
        for i in Family.objects.filter(Q(client=self) | Q(client_related=self)).order_by('-active', '-responsible', 'relation_level','client__person__name', 'client_related__person__name'):
            responsable = False
            id = i.client.id if not i.client == self else i.client_related.id
            name = i.client if not i.client == self else i.client_related
            dict = {}
            if not i.client == self:
                for x,y in FAMILY_RELATION_REVERSE:
                    dict[x] = y.__unicode__()
                relation_level = dict[i.relation_level]
            else:
                if i.responsible: responsable = True
                relation_level = i.get_relation_level_display()

            family_list.append([id, name, relation_level, responsable, i.id, i.active]) # id = client selected id, i.id = family relation id 
        
        return family_list
    
    def family_members_active(self):
        family_list = []
        for i in self.family_members():
            if i[5]:
                family_list.append(i)
        return family_list

    def is_company(self):
        return True if hasattr(self.person, 'company') else False

    def is_busy(self, start_time, end_time):
        ''' 
        check if client is busy in schedule for selected range
        filter 1: start time not in occurrence range
        filter 2: end time not in occurrence range
        filter 3: occurrence range are not between asked values
        note for exclude filters: 
            presence = 4 -> occurrence unmarked
            presence = 5 -> occurrence rescheduled
        '''

        from gestorpsi.schedule.models import ScheduleOccurrence
        queryset = ScheduleOccurrence.objects.filter(event__referral__client=self) \
            .exclude(occurrenceconfirmation__presence=4).exclude(occurrenceconfirmation__presence=5)

        return True if \
            queryset.filter(start_time__lte = start_time, end_time__gt = start_time) or \
            queryset.filter(start_time__lt = end_time, end_time__gte = end_time) or \
            queryset.filter(start_time__gte = start_time, end_time__lte = end_time) \
            else False

reversion.register(Client, follow=['person', ])
reversion.register(Family)

