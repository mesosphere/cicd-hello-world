resource "src-git": {
  type: "git"
  param url: "$(context.git.url)"
  param revision: "$(context.git.commit)"
}

task "release": {
  inputs: ["src-git"]

  steps: [
    {
      name: "test"
      image: "golang:1.13.0-buster"
      command: [ "go", "test", "./..." ]
      workingDir: "/workspace/src-git"
    }
  ]
}

actions: [
  {
    tasks: ["release"]
    on tag: {}
  }
]
