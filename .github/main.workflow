workflow "run tests" {
  on = "push"
	resolves = ["test"]
}

workflow "on pull request merge, delete the branch" {
  on = "pull_request"
  resolves = ["branch cleanup"]
}

action "branch cleanup" {
  uses = "jessfraz/branch-cleanup-action@master"
  secrets = ["GITHUB_TOKEN"]
}

action "test" {
  uses = "./"
	env = {
    SETTINGS = "settings"
  }
	args = ["manage", "test"]
}
