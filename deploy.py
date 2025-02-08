import subprocess
import boto3
import os
import shutil

# Configuration
BUCKET_NAME = "english-learning-artifacts"  # S3 bucket to store deployment artifacts
REGION = "us-east-1"
STACK_NAME = "EnglishLearningStack"
LAYER_NAME = "EnglishLearningDependencies"  # Name of the Lambda layer
LAYER_DIR = "dependencies_layer"  # Local folder for the layer content
PYTHON_VERSION = "python3.12"  # Target Python version for the layer
REQUIREMENTS = [
    "openai>=1.0.0",
    "pydantic",
    "pydantic-core",
    "typing-extensions",
    "annotated-types",
    "boto3",
]  # List of packages to include in the layer

# Initialize AWS S3 client
s3_client = boto3.client("s3", region_name=REGION)


def prepare_layer_directory(layer_dir, python_version, requirements):
    """
    Create the required folder structure
    and install dependencies into it.
    """
    if os.path.exists(layer_dir):
        print(
            f"Layer already exists '{layer_dir}' REUSING... (delete folder for reinstall packages)"
        )
        return

    target = os.path.join(layer_dir, "python", "lib", python_version, "site-packages")
    print(f"Creating layer directory structure at '{target}'...")
    os.makedirs(target, exist_ok=True)

    # Create requirements.txt file
    requirements_file = "requirements.txt"
    with open(requirements_file, "w") as f:
        for req in requirements:
            f.write(f"{req}\n")

    # Install all requirements at once to handle dependencies correctly
    print(f"Installing requirements into '{target}'...")
    subprocess.check_call(
        [
            "pip",
            "install",
            "-r",
            requirements_file,
            "-t",
            target,
            "--platform",
            "manylinux2014_x86_64",
            "--implementation",
            "cp",
            "--python-version",
            python_version.replace("python", "").replace(".", ""),
            "--only-binary=:all:",
            "--upgrade",
        ]
    )

    # Clean up requirements file
    os.remove(requirements_file)
    print("Layer directory prepared.")


def prepare_handlers_directory():
    """
    Create the handlers directory and ensure all Python files are present.
    """
    handlers_dir = "handlers"
    if not os.path.exists(handlers_dir):
        print(f"Creating handlers directory '{handlers_dir}'...")
        os.makedirs(handlers_dir)

    # Create __init__.py to make it a proper Python package
    init_file = os.path.join(handlers_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("")

    print("Handlers directory prepared.")


def bucket_exists(bucket_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except Exception:
        return False


def create_bucket(bucket_name, region):
    try:
        if region == "us-east-1":
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
        # Add versioning to the bucket
        s3_client.put_bucket_versioning(
            Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"}
        )
        print("Bucket versioning enabled.")
    except Exception as e:
        print(f"Error creating bucket: {str(e)}")
        raise


def package_and_deploy(bucket_name, region, stack_name):
    try:
        # Package the SAM template
        print("Packaging the SAM application...")
        subprocess.check_call(
            [
                "sam",
                "package",
                "--output-template-file",
                "packaged.yaml",
                "--s3-bucket",
                bucket_name,
            ]
        )
        # Deploy the packaged template
        print("Deploying the SAM application...")
        subprocess.check_call(
            [
                "sam",
                "deploy",
                "--template-file",
                "packaged.yaml",
                "--region",
                region,
                "--capabilities",
                "CAPABILITY_IAM",
                "CAPABILITY_NAMED_IAM",
                "CAPABILITY_AUTO_EXPAND",
                "--stack-name",
                stack_name,
                "--no-confirm-changeset",  # Skip confirmation for changesets
            ]
        )
    except subprocess.CalledProcessError as e:
        print(f"Error during packaging/deployment: {str(e)}")
        raise


def main():
    try:
        # Step 1: Prepare the handlers directory
        prepare_handlers_directory()

        # Step 2: Prepare the layer directory with required dependencies
        prepare_layer_directory(LAYER_DIR, PYTHON_VERSION, REQUIREMENTS)

        # Step 3: Ensure the S3 bucket exists
        if not bucket_exists(BUCKET_NAME):
            print(f"Bucket '{BUCKET_NAME}' does not exist. Creating it...")
            create_bucket(BUCKET_NAME, REGION)
            print(f"Bucket '{BUCKET_NAME}' created.")
        else:
            print(f"Bucket '{BUCKET_NAME}' already exists.")

        # Step 4: Package and deploy the SAM application
        package_and_deploy(BUCKET_NAME, REGION, STACK_NAME)
        print("Deployment completed successfully.")

    except Exception as e:
        print(f"Deployment failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
