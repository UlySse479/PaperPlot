"""Built-in publication profiles."""

from paperplot.profiles.acl import PROFILE as ACL_PROFILE
from paperplot.profiles.cvpr import PROFILE as CVPR_PROFILE
from paperplot.profiles.emnlp import PROFILE as EMNLP_PROFILE
from paperplot.profiles.icml import PROFILE as ICML_PROFILE
from paperplot.profiles.nature import PROFILE as NATURE_PROFILE
from paperplot.profiles.neurips import PROFILE as NEURIPS_PROFILE


PROFILES = {
    "icml": ICML_PROFILE,
    "neurips": NEURIPS_PROFILE,
    "acl": ACL_PROFILE,
    "cvpr": CVPR_PROFILE,
    "emnlp": EMNLP_PROFILE,
    "nature": NATURE_PROFILE,
}

__all__ = ["PROFILES"]
