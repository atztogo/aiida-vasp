"""Test aiida_parameters."""
# pylint: disable=unused-import,redefined-outer-name,unused-argument,unused-wildcard-import,wildcard-import,no-member, import-outside-toplevel

import pytest

from aiida.common.extendeddicts import AttributeDict

from aiida_vasp.assistant.parameters import ParametersMassage


@pytest.fixture
def init_relax_parameters():
    """Fixture for a set of general input parameters for relaxation."""
    general_parameters = AttributeDict()
    general_parameters.relax = AttributeDict()
    general_parameters.relax.algo = 'cg'
    general_parameters.relax.energy_cutoff = 0.01
    general_parameters.relax.force_cutoff = 0.01
    general_parameters.relax.steps = 60
    general_parameters.relax.positions = True
    general_parameters.relax.shape = True
    general_parameters.relax.volume = True

    return general_parameters


@pytest.fixture
def init_smearing_parameters():
    """Fixture for a set of general input parameters regarding Fermi integral smearing."""
    general_parameters = AttributeDict()
    general_parameters.smearing = AttributeDict()
    general_parameters.smearing.gaussian = True

    return general_parameters


@pytest.fixture
def init_charge_parameters():
    """Fixture for a set of general input parameters regarding how to construct initial charge density."""
    general_parameters = AttributeDict()
    general_parameters.charge = AttributeDict()
    general_parameters.charge.constant_charge = True

    return general_parameters


@pytest.fixture
def init_bands_parameters():
    """Fixture for a set of general input parameters for band structure calculations."""
    general_parameters = AttributeDict()
    general_parameters.bands = AttributeDict()
    general_parameters.bands.decompose_bands = False
    general_parameters.bands.decompose_wave = False

    return general_parameters


@pytest.fixture
def init_simple_workchain():
    """Fixture to simulate a fake workchain to store the exit codes and a dummy report function."""
    workchain = AttributeDict()
    workchain.exit_codes = AttributeDict()
    workchain.exit_codes.ERROR_INVALID_PARAMETER_DETECTED = 1
    workchain.exit_codes.ERROR_MISSING_PARAMETER_DETECTED = 1
    workchain.report = print

    return workchain


def test_relax_parameters_all_set(init_relax_parameters):
    """Test all standard relaxation parameters are set."""
    massager = ParametersMassage(None, init_relax_parameters)
    assert massager.exit_code is None
    parameters = massager.parameters.vasp
    assert parameters.ediffg == -0.01
    assert parameters.ibrion == 2
    assert parameters.nsw == 60
    assert parameters.isif == 3


def test_catch_invalid_tags(init_relax_parameters, init_simple_workchain):
    init_relax_parameters.vasp = AttributeDict()
    mock_workchain = init_simple_workchain
    init_relax_parameters.vasp.smear = 1  # This is an invalid tag
    massager = ParametersMassage(mock_workchain, init_relax_parameters)
    assert massager.exit_code is not None


def test_relax_parameters_energy(init_relax_parameters):
    """Test no provided force cutoff. It should be set to a default value."""
    del init_relax_parameters.relax.force_cutoff
    massager = ParametersMassage(None, init_relax_parameters)
    assert massager.exit_code is None
    parameters = massager.parameters.vasp
    assert parameters.ediffg == 0.01


def test_relax_parameters_no_algo(init_relax_parameters, init_simple_workchain):
    """Test no provided algo tag."""
    mock_workchain = init_simple_workchain
    del init_relax_parameters.relax.algo
    massager = ParametersMassage(mock_workchain, init_relax_parameters)
    assert massager.exit_code is not None


def test_relax_parameters_vol_shape(init_relax_parameters):
    """Test volume and shape relaxation combinations."""
    del init_relax_parameters.relax.positions
    massager = ParametersMassage(None, init_relax_parameters)
    assert massager.exit_code is None
    parameters = massager.parameters.vasp
    assert parameters.isif == 6


def test_relax_parameters_pos_shape(init_relax_parameters):
    """Test position and shape relxation combinations."""
    del init_relax_parameters.relax.volume
    massager = ParametersMassage(None, init_relax_parameters)
    assert massager.exit_code is None
    parameters = massager.parameters.vasp
    assert parameters.isif == 4


def test_relax_parameters_vol(init_relax_parameters):
    """Test only volume relaxation."""
    del init_relax_parameters.relax.positions
    del init_relax_parameters.relax.shape
    massager = ParametersMassage(None, init_relax_parameters)
    assert massager.exit_code is None
    parameters = massager.parameters.vasp
    assert parameters.isif == 7


def test_relax_parameters_pos(init_relax_parameters):
    """Test only position relaxation."""
    del init_relax_parameters.relax.volume
    del init_relax_parameters.relax.shape
    massager = ParametersMassage(None, init_relax_parameters)
    assert massager.exit_code is None
    parameters = massager.parameters.vasp
    assert parameters.isif == 2


def test_relax_parameters_shape(init_relax_parameters):
    """Test only shape relaxation."""
    del init_relax_parameters.relax.volume
    del init_relax_parameters.relax.positions
    massager = ParametersMassage(None, init_relax_parameters)
    assert massager.exit_code is None
    parameters = massager.parameters.vasp
    assert parameters.isif == 5


def test_relax_parameters_nothing(init_relax_parameters):
    """Test if no relaxation parameters for volume, positions and shape are given."""
    del init_relax_parameters.relax.volume
    del init_relax_parameters.relax.positions
    del init_relax_parameters.relax.shape
    massager = ParametersMassage(None, init_relax_parameters)
    assert massager.exit_code is None
    parameters = massager.parameters.vasp
    assert parameters == AttributeDict()


def test_relax_parameters_override(init_relax_parameters):
    """Test what happens if we override a parameters."""
    value = 1
    init_relax_parameters.isif = value
    massager = ParametersMassage(None, init_relax_parameters)
    assert massager.exit_code is None
    parameters = massager.parameters.vasp
    assert parameters.isif == value


def test_smearing_parameters():
    """Test smearing parameters."""
    parameters = AttributeDict()
    parameters.smearing = AttributeDict()
    parameters.smearing.gaussian = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.ismear == 0
    parameters.smearing.gaussian = False
    parameters.smearing.fermi = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.ismear == -1
    parameters.smearing.fermi = False
    parameters.smearing.tetra = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.ismear == -5
    parameters.smearing.tetra = False
    parameters.smearing.mp = 4
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.ismear == 4


def test_charge_parameters():
    """Test charge parameters."""
    parameters = AttributeDict()
    parameters.charge = AttributeDict()
    parameters.charge.from_wave = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    parameters.charge.from_wave = False
    parameters.charge.from_charge = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.icharg == 1
    parameters.charge.from_charge = False
    parameters.charge.from_atomic = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.icharg == 2
    parameters.charge.from_atomic = False
    parameters.charge.from_potential = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.icharg == 4
    parameters.charge.from_potential = False
    parameters.charge.constant_charge = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.icharg == 11
    parameters.charge.constant_charge = False
    parameters.charge.constant_atomic = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.icharg == 12


def test_orbital_projections():  # pylint: disable=too-many-statements
    """Test the parameters associated with orbital projections."""
    parameters = AttributeDict()
    parameters.bands = AttributeDict()
    parameters.bands.decompose_wave = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.lorbit == 5
    parameters.bands.decompose_wave = False
    parameters.bands.decompose_bands = True
    parameters.bands.decompose_auto = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.lorbit == 14
    parameters.bands.decompose_auto = False
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.lorbit == 10
    parameters.bands.lm = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.lorbit == 11
    parameters.bands.phase = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.lorbit == 12
    parameters.bands.lm = False
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.lorbit == 12

    # Now do the once with a Wigner-Seitz radius supplied
    parameters.bands.wigner_seitz_radius = [2.0]
    parameters.bands.lm = False
    parameters.bands.phase = False
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.lorbit == 0
    assert int(massager.parameters.vasp.rwigs[0]) == 2
    parameters.bands.lm = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.lorbit == 1
    parameters.bands.phase = True
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.lorbit == 2
    parameters.bands.lm = False
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.lorbit == 2

    # Should raise ValueError if Wigner-Seitz radius is not defined as a list.
    parameters.bands.wigner_seitz_radius = 2.0
    with pytest.raises(ValueError):
        massager = ParametersMassage(None, parameters)


def test_vasp_parameter_override(init_relax_parameters):
    """Test of the override functionality works as intended."""
    init_relax_parameters.vasp = AttributeDict()
    # Redefine to from 3 to 0.
    init_relax_parameters.vasp.isif = 0
    massager = ParametersMassage(None, init_relax_parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.isif == 0


def test_inherit_and_merge():
    """Test the inherit and merge functionality for the parameters and inputs."""
    from aiida.plugins import DataFactory
    from aiida_vasp.assistant.parameters import inherit_and_merge_parameters

    inputs = AttributeDict()
    inputs.bands = AttributeDict()
    inputs.bands.somekey = DataFactory('bool')(True)
    inputs.relax = AttributeDict()
    inputs.relax.somekey = DataFactory('bool')(True)
    inputs.smearing = AttributeDict()
    inputs.smearing.somekey = DataFactory('bool')(True)
    inputs.charge = AttributeDict()
    inputs.charge.somekey = DataFactory('bool')(True)
    inputs.converge = AttributeDict()
    inputs.converge.somekey = DataFactory('bool')(True)
    inputs.electronic = AttributeDict()
    inputs.electronic.somekey = DataFactory('bool')(True)
    inputs.dynamics = AttributeDict()
    inputs.dynamics.somekey = DataFactory('bool')(True)
    # Check that parameters does not have to be present
    parameters = inherit_and_merge_parameters(inputs)
    # Check that an empty parameters is allowed
    inputs.parameters = DataFactory('dict')(dict={})
    parameters = inherit_and_merge_parameters(inputs)
    test_parameters = AttributeDict({
        'vasp': AttributeDict(),
        'electronic': AttributeDict({'somekey': True}),
        'bands': AttributeDict({'somekey': True}),
        'smearing': AttributeDict({'somekey': True}),
        'charge': AttributeDict({'somekey': True}),
        'relax': AttributeDict({'somekey': True}),
        'converge': AttributeDict({'somekey': True}),
        'dynamics': AttributeDict({'somekey': True})
    })
    assert parameters == test_parameters
    # Test ignored
    inputs.ignored = AttributeDict()
    inputs.ignored.ignored = DataFactory('bool')(True)
    parameters = inherit_and_merge_parameters(inputs)
    assert parameters == test_parameters
    # Test to override inputs.bands.somekey
    inputs.parameters = DataFactory('dict')(dict={'bands': {'somekey': False}})
    parameters = inherit_and_merge_parameters(inputs)
    test_parameters.bands.somekey = False
    assert parameters == test_parameters


def test_unsupported_fail_override():
    """Test that any supplied unsupported parameters in the regular parameters dictionary yield error."""
    parameters = AttributeDict()
    parameters.vasp = AttributeDict()
    parameters.vasp.not_valid = 200
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code


def test_unsupported_fail():
    """Test that any supplied unsupported parameters in the regular overload parameters dictionary does not yield an error."""
    parameters = AttributeDict()
    parameters.not_valid = 200
    massager = ParametersMassage(None, parameters)
    # The not valid parameter was never set as there is no setter function for it.
    assert massager.parameters.vasp == {}


def test_unsupported_parameters():
    """Test that it is possibly to supply unsupported parameters."""
    parameters = AttributeDict()
    parameters.not_valid = 200
    massager = ParametersMassage(
        None,
        parameters,
        unsupported_parameters={'not_valid': {
            'default': 1.0,
            'description': 'Something',
            'type': float,
            'values': [1.0, 2.0]
        }})
    assert massager.exit_code is None
    assert massager.parameters.vasp.not_valid == parameters.not_valid


def test_pwcutoff_to_encut():
    """Test that the pwcutoff is converted to encut."""
    parameters = AttributeDict()
    parameters.pwcutoff = 200
    massager = ParametersMassage(None, parameters)
    assert massager.exit_code is None
    assert massager.parameters.vasp.encut == parameters.pwcutoff
