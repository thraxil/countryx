workflow "run tests" {
  on = "push"
  resolves = ["docker push"]
}

workflow "on pull request merge, delete the branch" {
  on = "pull_request"
  resolves = ["branch cleanup"]
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

action "Deploy branch filter" {
  uses = "actions/bin/filter@master"
  args = "branch master"
}

action "docker push" {
  needs = ["docker login", "Build docker image", "Deploy branch filter"]
  uses = "actions/docker/cli@master"
  args = ["push", "thraxil/countryx"]
}
