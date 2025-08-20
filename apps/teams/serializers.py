from rest_framework import serializers
from .models import Team, TeamMembership, TeamProject
from apps.users.serializers import UserSerializer

class TeamMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = TeamMembership
        fields = ['id', 'user', 'user_id', 'role', 'is_active', 'joined_at']
        read_only_fields = ['id', 'joined_at']

class TeamProjectSerializer(serializers.ModelSerializer):
    responsible = UserSerializer(read_only=True)
    responsible_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = TeamProject
        fields = ['id', 'name', 'description', 'responsible', 'responsible_id',
                 'start_date', 'target_end_date', 'actual_end_date', 'status',
                 'is_overdue', 'created_at']
        read_only_fields = ['id', 'created_at']

class TeamListSerializer(serializers.ModelSerializer):
    leader = UserSerializer(read_only=True)
    member_count = serializers.ReadOnlyField()
    active_tarjetas_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'leader', 'member_count', 
                 'active_tarjetas_count', 'is_active', 'created_at']

class TeamDetailSerializer(serializers.ModelSerializer):
    leader = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    memberships = TeamMembershipSerializer(many=True, read_only=True)
    projects = TeamProjectSerializer(many=True, read_only=True)
    member_count = serializers.ReadOnlyField()
    active_tarjetas_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'leader', 'created_by', 
                 'memberships', 'projects', 'member_count', 'active_tarjetas_count',
                 'is_active', 'created_at', 'updated_at']

class TeamCreateSerializer(serializers.ModelSerializer):
    leader_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Team
        fields = ['name', 'description', 'leader_id', 'member_ids']
    
    def create(self, validated_data):
        leader_id = validated_data.pop('leader_id', None)
        member_ids = validated_data.pop('member_ids', [])
        
        validated_data['created_by'] = self.context['request'].user
        
        if leader_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                leader = User.objects.get(id=leader_id)
                validated_data['leader'] = leader
            except User.DoesNotExist:
                raise serializers.ValidationError({'leader_id': 'Usuario no encontrado'})
        
        team = super().create(validated_data)
        
        # Agregar miembros
        for member_id in member_ids:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=member_id)
                TeamMembership.objects.create(
                    team=team,
                    user=user,
                    added_by=self.context['request'].user
                )
            except User.DoesNotExist:
                continue  # Ignorar usuarios no encontrados
        
        return team