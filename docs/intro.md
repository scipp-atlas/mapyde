# Introduction

---

## Configuration

All project-specific configuration recognized by mapyde can be defined in a
custom `user.toml`:

=== ":octicons-file-code-16: default"

    ```toml
    [base]
    path = "/data/users/{{USER}}/SUSY"
    output = "mytag"
    template = "{{MAPYDE_TEMPLATES}}/defaults.toml"

    [madgraph.proc]
    name = "charginos"
    card = "{{madgraph['proc']['name']}}"

    [madgraph.masses]
    MN1 = 100
    MC1 = 150
    ```

=== ":octicons-file-code-16: ewkinos"

    ```toml
    [base]
    path = "/data/users/{{USER}}/SUSY"
    output = "mytag"
    template = "{{MAPYDE_TEMPLATES}}/ewkinos.toml"

    [madgraph.proc]
    name = "isr2L"
    card = "{{madgraph['proc']['name']}}"

    [madgraph.masses]
    MN2 = 250
    MC1 = 250
    MN1 = 240
    ```

=== ":octicons-file-code-16: sleptons"

    ```toml
    [base]
    path = "/data/users/{{USER}}/SUSY"
    output = "mytag"
    template = "{{MAPYDE_TEMPLATES}}/sleptons.toml"

    [madgraph.proc]
    name = "isrslep"
    card = "{{madgraph['proc']['name']}}"

    [madgraph.masses]
    MSLEP = 250
    MN1 = 240
    ```

<!-- prettier-ignore -->
!!! tip
    This is all highly customizable with the usage of templates to make it easier to inherit a _convenient_ set of defaults for which you can override.
