from django.db import transaction
from rest_framework import serializers

from api.utils import pypiclient

from .models import PackageRelease, Project


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageRelease
        fields = ['name', 'version']
        extra_kwargs = {'version': {'required': False}}


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'packages']

    packages = PackageSerializer(many=True)

    def create(self, validated_data):

        received_packages = validated_data["packages"]

        received_packages = PackageSerializer(data=received_packages, many=True)
        received_packages.is_valid(raise_exception=True)

        packages = []
        for package in received_packages.data:
            package_data = pypiclient.getPackageOr404(
                package.get("name"), package.get("version")
            )
            if not package_data["exists"]:
                raise serializers.ValidationError(
                    {"error": "One or more packages doesn't exist"}
                )
            else:
                packages.append(
                    {
                        "name": package_data["package"]["name"],
                        "version": package_data["version"],
                    }
                )

        project = Project(name=validated_data.get("name"))
        project.save()

        save_packages(packages, project)

        return ProjectSerializer(project).data


@transaction.atomic()
def save_packages(packages: list, project: Project):
    for package in packages:
        PackageRelease(
            project=project, name=package["name"], version=package["version"]
        ).save()
