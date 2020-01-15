resource "src-git": {
  type: "git"
  param url: "$(context.git.url)"
  param revision: "$(context.git.commit)"
}

resource "gitops-git": {
  type: "git"
  param url: "https://github.com/cprovencher/cicd-hello-world-gitops"
}

task "release": {
  inputs: ["gitops-git"]
  steps: [
    {
      name: "update-gitops-repo"
      image: "mesosphere/update-gitops-repo:v1.0"
      workingDir: "/workspace/gitops-git"
      args: [
        "-git-revision=$(context.git.commit)",
        "-substitute=releaseUrl=//ok//$(context.git.tag)//ok//"
      ]
    }
  ]
}

actions: [
  {
    tasks: ["release"]
    on tag names: ["v*"]
  }
]
