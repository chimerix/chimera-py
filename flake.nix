{
  inputs.nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";

  outputs =
    inputs:
    let
      forSystem = inputs.nixpkgs.lib.genAttrs [
        "x86_64-linux"
        "aarch64-linux"
      ];
      pkgsFor = forSystem (system: import inputs.nixpkgs { inherit system; });
    in
    {
      devShells = forSystem (
        system:
        let
          pkgs = pkgsFor."${system}";
        in
        {
          default = pkgs.mkShell {
            venvDir = ".venv";
            buildInputs = [
              pkgs.just
              pkgs.uv
              pkgs.python313
              pkgs.python313Packages.venvShellHook
            ];
          };
        }
      );
    };
}
