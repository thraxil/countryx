workflow "run tests" {
  on = "push"
  resolves = ["Build docker image"]
}

workflow "on pull request merge, delete the branch" {
  on = "pull_request"
  resolves = ["branch cleanup", "docker push"]
}

action "branch cleanup" {
  uses = "jessfraz/branch-cleanup-action@master"
  secrets = ["GITHUB_TOKEN"]
}

action "docker login" {
  uses = "actions/docker/login@master"
  secrets = ["DOCKER_USERNAME", "DOCKER_PASSWORD"]
}

action "Build docker image" {
  uses = "actions/docker/cli@master"
  args = "build -t thraxil/countryx ."
}

action "docker push" {
  needs = ["docker login", "Build docker image"]
  uses = "actions/docker/cli@master"
  args = ["push", "thraxil/countryx"]
}
