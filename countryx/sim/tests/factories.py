from datetime import datetime
import factory
from django.contrib.auth.models import User
from countryx.sim.models import (
    Role, State, StateChange, StateVariable,
    StateRoleChoice, Section,
    SectionGroup, SectionAdministrator,
    SectionGroupPlayer, SectionGroupState,
    SectionGroupPlayerTurn,
)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: "user%d" % n)


class RoleFactory(factory.DjangoModelFactory):
    class Meta:
        model = Role
    name = factory.Sequence(lambda n: 'role {0}'.format(n))


class StateFactory(factory.DjangoModelFactory):
    class Meta:
        model = State
    name = factory.Sequence(lambda n: 'state {0}'.format(n))
    turn = 0
    state_no = 0


class StateChangeFactory(factory.DjangoModelFactory):
    class Meta:
        model = StateChange
    state = factory.SubFactory(StateFactory)
    roles = ('{"President": 0, "FirstWorldEnvoy": 1, '
             '"SubRegionalRep": 2, "OppositionLeadership": 3}')
    next_state = factory.SubFactory(StateFactory)


class StateVariableFactory(factory.DjangoModelFactory):
    class Meta:
        model = StateVariable
    state = factory.SubFactory(StateFactory)
    name = factory.Sequence(lambda n: 'variable {0}'.format(n))


class StateRoleChoiceFactory(factory.DjangoModelFactory):
    class Meta:
        model = StateRoleChoice
    state = factory.SubFactory(StateFactory)
    role = factory.SubFactory(RoleFactory)
    choice = 0
    desc = ""


class SectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Section
    name = factory.Sequence(lambda n: 'section {0}'.format(n))
    created_date = datetime.now()
    turn = 1


class SectionGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = SectionGroup
    section = factory.SubFactory(SectionFactory)
    name = factory.Sequence(lambda n: 'group {0}'.format(n))


class SectionAdministratorFactory(factory.DjangoModelFactory):
    class Meta:
        model = SectionAdministrator
    section = factory.SubFactory(SectionFactory)
    user = factory.SubFactory(UserFactory)


class SectionGroupPlayerFactory(factory.DjangoModelFactory):
    class Meta:
        model = SectionGroupPlayer

    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(SectionGroupFactory)
    role = factory.SubFactory(RoleFactory)


class SectionGroupPlayerTurnFactory(factory.DjangoModelFactory):
    class Meta:
        model = SectionGroupPlayerTurn

    player = factory.SubFactory(SectionGroupPlayerFactory)
    turn = 1
    choice = 1
    faculty = factory.SubFactory(SectionAdministratorFactory)


class SectionGroupStateFactory(factory.DjangoModelFactory):
    class Meta:
        model = SectionGroupState
    state = factory.SubFactory(StateFactory)
    group = factory.SubFactory(SectionGroupFactory)
    date_updated = datetime.now()
