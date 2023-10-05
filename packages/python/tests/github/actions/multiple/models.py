from m.github.actions import InArg, KebabModel


class GithubInputs(KebabModel):
    arg_1: str = InArg(help='arg 1')
    arg_2: str = InArg(help='arg 2')
    arg_3: str = InArg(help='arg 3', default='no_need_to_specify')
