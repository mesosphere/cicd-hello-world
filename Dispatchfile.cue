resource "src-git": {
  type: "git"
  param url: "$(context.git.url)"
  param revision: "$(context.git.commit)"
  param paths: ["hello"]
}

resource "gitops-git": {
  type: "git"
  param url: "https://github.com/cprovencher/cicd-hello-world-gitops"
}

task "upgrade-soak": {
  inputs: ["gitops-git"]
  steps: [
    {
      name: "fetch-master"
      image: "alpine/git"
      workingDir: "/workspace/gitops-git"
      args: [
        "fetch", "origin", "master"
      ]
    },
    {
      name: "update-gitops-repo"
      image: "mesosphere/update-gitops-repo:v1.0"
      workingDir: "/workspace/gitops-git"
      args: [
        "-git-revision=$(context.git.commit)",
        "-substitute=konvoyVersion=$(context.git.tag)"
      ]
    }
  ]
}

actions: [
  {
    tasks: ["upgrade-soak"]
    on push: {
      branches: ["*"]
    }
  }
]
