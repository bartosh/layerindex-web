from models import Branch, LayerItem, LayerNote, LayerBranch, LayerDependency, Recipe, Machine
from rest_framework import viewsets, serializers
from querysethelper import params_to_queryset, get_search_tuple

class ParametricSearchableModelViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        model = self.__class__.serializer_class.Meta.model
        qs = model.objects.all()
        (filter_string, search_term, ordering_string) = get_search_tuple(self.request, model)
        return params_to_queryset(model, qs, filter_string, search_term, ordering_string)

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch

class BranchViewSet(ParametricSearchableModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

class LayerItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LayerItem

class LayerItemViewSet(ParametricSearchableModelViewSet):
    queryset = LayerItem.objects.all()
    serializer_class = LayerItemSerializer

class LayerBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = LayerBranch

class LayerBranchViewSet(ParametricSearchableModelViewSet):
    queryset = LayerBranch.objects.all()
    serializer_class = LayerBranchSerializer

class LayerDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = LayerDependency

class LayerDependencyViewSet(ParametricSearchableModelViewSet):
    queryset = LayerDependency.objects.all()
    serializer_class = LayerDependencySerializer

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe

class RecipeViewSet(ParametricSearchableModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine

class MachineViewSet(ParametricSearchableModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
