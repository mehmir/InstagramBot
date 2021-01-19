from DAL.repositories import InstaUserRepository
from DAL.repositories import TargetPageRepository
from DAL.repositories import WorkPageRepository



def userInsta_repository():
    return InstaUserRepository()


def workPage_repository():
    return WorkPageRepository()


def objectives_repository():
    return TargetPageRepository()
