{
  description = "Python support for [MC-NBFX]: .NET Binary Format: XML Data Structure";

  inputs = {
    nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*.tar.gz";

   pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      nixpkgs,
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,
      ...
    }:
    let inherit (nixpkgs) lib;

      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

      # Create package overlay from workspace.
      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel"; 
      };
    

      # Extend generated overlay with build fixups
      #
      # Uv2nix can only work with what it has, and uv.lock is missing essential metadata to perform some builds.
      # This is an additional overlay implementing build fixups.
      # See:
      # - https://pyproject-nix.github.io/uv2nix/FAQ.html
      pyprojectOverrides = _final: _prev: {
        # Implement build fixups here.
      };


      # This example is only using x86_64-linux
      pkgs = nixpkgs.legacyPackages.x86_64-linux;

      # Use Python 3.12 from nixpkgs
      python = pkgs.python312;
  


      # Construct package set
      pythonSet =
        # Use base package set from pyproject.nix builders
        (pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
        }).overrideScope
          (
            lib.composeManyExtensions [
              pyproject-build-systems.overlays.default
              overlay
              pyprojectOverrides
            ]
          );
    
    in {

      # Enable no optional dependencies for production build.
      packages.x86_64-linux.default = pythonSet.mkVirtualEnv "pynbfx-env" workspace.deps.default;


      devShells.x86_64-linux = {
        uv2nix =
          let
            # Create an overlay enabling editable mode for all local dependencies.
            editableOverlay = workspace.mkEditablePyprojectOverlay {
              # Use environment variable
              root = "$REPO_ROOT";
              # Optional: Only enable editable for these packages
              # members = [ "pynbfx" ];
            };

            # Override previous set with our overrideable overlay.
            editablePythonSet = pythonSet.overrideScope editableOverlay;

            # Build virtual environment, with local packages being editable.
            #
            # Enable all optional dependencies for development.
            virtualenv = editablePythonSet.mkVirtualEnv "pynbfx-dev-env" workspace.deps.all;

          in
          pkgs.mkShell {
            packages = [
              virtualenv
              pkgs.uv
            ];
            shellHook = ''
              # Undo dependency propagation by nixpkgs.
              unset PYTHONPATH
              # Get repository root using git. This is expanded at runtime by the editable `.pth` machinery.
              export REPO_ROOT=$(git rev-parse --show-toplevel)
              export UV_NO_SYNC=1
            '';
          };
      };



  };
}
