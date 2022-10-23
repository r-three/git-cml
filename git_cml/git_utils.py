import git
import os
import json
import logging
import io
import torch
import subprocess


def get_git_repo():
    """
    Create a git.Repo object for this repository

    Returns
    -------
    git.Repo
        Repo object for the current git repository
    """
    return git.Repo(os.getcwd(), search_parent_directories=True)


def create_git_cml(repo):
    """
    If not already created, create $git_root/.git_cml and return path

    Parameters
    ----------
    git_root : str
        path to git repository's root directory

    Returns
    -------
    str
        path to $git_root/.git_cml directory
    """
    git_cml = os.path.join(repo.working_dir, ".git_cml")
    if not os.path.exists(git_cml):
        logging.debug(f"Creating git cml directory {git_cml}")
        os.makedirs(git_cml)
    return git_cml


def create_git_cml_model_dir(repo, model_path):
    """
    If not already created, create directory under $git_root/.git_cml/ to store a model and return path

    Parameters
    ----------
    repo : git.Repo
        Repo object for the current git repository

    model_path : str
        path to model file being saved

    Returns
    -------
    str
        path to $git_root/.git_cml/$model_name directory
    """
    git_cml = create_git_cml(repo)
    model_file = os.path.basename(model_path)
    git_cml_model = os.path.join(git_cml, os.path.splitext(model_file)[0])

    if not os.path.exists(git_cml_model):
        logging.debug(f"Creating model directory {git_cml_model}")
        os.makedirs(git_cml_model)
    return git_cml_model


def get_gitattributes_file(repo):
    """
    Get path to this repo's .gitattributes file

    Parameters
    ----------
    repo : git.Repo
        Repo object for the current git repository

    Returns
    -------
    str
        path to $git_root/.gitattributes
    """
    return os.path.join(repo.working_dir, ".gitattributes")


def read_gitattributes(gitattributes_file):
    """
    Read contents of this repo's .gitattributes file

    Parameters
    ----------
    gitattributes_file : str
        Path to this repo's .gitattributes file

    Returns
    -------
    List[str]
        lines in .gitattributes file
    """
    if os.path.exists(gitattributes_file):
        with open(gitattributes_file, "r") as f:
            return f.readlines()
    else:
        return []


def write_gitattributes(gitattributes_file, attributes):
    """
    Write list of attributes to this repo's .gitattributes file

    Parameters
    ----------
    gitattributes_file : str
        Path to this repo's .gitattributes file

    attributes : List[str]
        Attributes to write to .gitattributes
    """
    with open(gitattributes_file, "w") as f:
        f.writelines(attributes)


def load_tracked_file(f):
    """
    TODO: currently expects pytorch format but should migrate to TensorStore
    Load tracked file

    Parameters
    ----------
    f : str
        path to file tracked by git-cml filter

    Returns
    -------
    dict
        contents of file

    """
    logging.debug(f"Loading tracked file {f}")
    return torch.load(f)


def write_tracked_file(f, param):
    """
    Dump param into tracked file
    TODO: currently dumps as pytorch format but should migrate to TensorStore

    Parameters
    ----------
    f : str
        path to output file
    param : list or scalar
        param value to dump to file

    """
    logging.debug(f"Dumping param to {f}")
    torch.save(param, f)


def load_staged_file(f):
    """
    Load staged file

    Parameters
    ----------
    f : str or file-like object
        staged file to load

    Returns
    -------
    dict
        staged file contents
    """
    if isinstance(f, io.IOBase):
        return json.load(f)
    else:
        with open(f, "r") as f:
            return json.load(f)


def write_staged_file(f, contents):
    """
    Write staged file

    Parameters
    ----------
    f : str or file-like object
        file to write staged contents to
    contents : dict
        dictionary to write to staged file
    """
    if isinstance(f, io.IOBase):
        json.dump(contents, f, indent=4)
    else:
        with open(f, "w") as f:
            json.dump(contents, f, indent=4)


def add_file(f, repo):
    """
    Add file to git staging area

    Parameters
    ----------
    f : str
        path to file
    repo : git.Repo
        Repo object for current git repository
    """
    logging.debug(f"Adding {f} to staging area")
    repo.git.add(f)


def git_lfs_install():
    """
    Run the `git lfs install` command

    Returns
    -------
    int
        Return code of `git lfs install`
    """
    out = subprocess.run(["git", "lfs", "install"])
    return out.returncode


def git_lfs_track(repo, directory):
    """
    Run the `git lfs track` command to track the files under `directory`

    Parameters
    ----------
    repo : git.Repo
        Repo object for current git repository
    directory : str
        Track all files under this directory

    Returns
    -------
    int
        Return code of `git lfs track`
    """
    track_glob = os.path.relpath(os.path.join(directory, "**"), repo.working_dir)
    out = subprocess.run(["git", "lfs", "track", f'"{track_glob}"'])
    return out.returncode
