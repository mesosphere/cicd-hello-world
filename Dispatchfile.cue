resource "src-git": {
  type: "git"
  param url: "$(context.git.url)"
  param revision: "$(context.git.commit)"
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
      image: "mesosphere/update-gitops-repo:1.2.0-beta1-69-g8b7a421c"
      workingDir: "/workspace/gitops-git"
      args: [
        "-git-revision=$(context.git.commit)",
        "-substitute=replaceThis=$(context.git.commit)",
        "-branch=master",
        "-create-pull-request=false",
        "-commit-message=\"Deploy soak update\"",
        "-merge-pull-request=true"
      ]
    }
  ]
}

task "script-exec": {
  steps: [
    {
      name: "check-script"
      image: "busybox:latest"
      workingDir: "/workspace/src-git"
      command: ["./magicfile"]
      args: [
         "asdf", "zxcv"
      ]
    }
  ]
}


actions: [
  {
    tasks: ["script-exec"]
    on push: {
      branches: ["*"]
    }
  }
]
