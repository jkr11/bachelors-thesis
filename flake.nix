{
  description = "Bachlors thesis reproducible build";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        
        texlive = pkgs.texliveSmall.withPackages (ps: with ps; [
          #scheme-medium
          latexmk
          biber
          biblatex
          luatex
          lualatex-math
          collection-latexextra
          collection-fontsrecommended
          collection-bibtexextra
          fontspec  
          newtx
          libertine
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [ texlive ];
          shellHook = ''
            echo "..."
          '';
        };

        packages.default = pkgs.stdenvNoCC.mkDerivation {
          pname = "main";
          version = "0.1.0";
          src = ./.;

          buildInputs = [ texlive ];

          ## TODO: set system date.
          buildPhase = ''
            export HOME=$TMPDIR
            cd tex

            latexmk -pdflua -interaction=nonstopmode -file-line-error main.tex
          '';

          installPhase = ''
            mkdir -p $out
            cp main.pdf $out/
          '';
        };
      });
}