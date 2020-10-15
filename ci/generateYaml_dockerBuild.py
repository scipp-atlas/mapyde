#!/usr/bin/env python3
import argparse
import pathlib
import json


def make_job(dockerfile_path):
    job_name = dockerfile_path.stem
    print(f"Building config for build_{job_name}")
    return {
        f"build_{job_name}": {
            "image": {
                "name": "gitlab-registry.cern.ch/ci-tools/docker-image-builder",
                "entrypoint": [""],
            },
            "script": [
                'echo "{"auths":{"$CI_REGISTRY":{"username":"$CI_REGISTRY_USER","password":"$CI_REGISTRY_PASSWORD"}}}" > /kaniko/.docker/config.json',
                f'/kaniko/executor --context "${{CI_PROJECT_DIR}}" --dockerfile "{dockerfile_path.resolve()}" --destination "${{CI_REGISTRY_IMAGE}}/{job_name}:${{CI_COMMIT_REF_SLUG}}"',
            ],
        }
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build CI configs for dockerfiles.")
    parser.add_argument(
        "files",
        metavar="f",
        type=pathlib.Path,
        nargs="+",
        help="paths for dockerfiles to build",
    )
    parser.add_argument("--output-file", default=None, help="Output file to write to")
    args = parser.parse_args()

    config = {}
    for f in args.files:
        config.update(make_job(f))

    if args.output_file is None:
        print(json.dumps(config, indent=4, sort_keys=True))
    else:
        with open(args.output_file, "w+") as out_file:
            json.dump(config, out_file, indent=4, sort_keys=True)
