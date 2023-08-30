from rest_framework import serializers
from apps.account.models import Account
from apps.competition.models import Category, Competition, CompetitionMaps, Participant, CompetitionTexts


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'icon')


class CompetitionTextsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionTexts
        fields = ('id', 'competition', 'title', 'description')


class CompetitionMapsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionMaps
        fields = ('id', 'competition', 'maps', 'title')


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ('id', 'user', 'choice', 'personal_id', 'duration')


class BannerParticipantsSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        request = self.context.get('request')
        if request and obj.user.avatar:
            return request.build_absolute_uri(obj.user.avatar.url)
        return None

    class Meta:
        model = Participant
        fields = ('id', 'avatar')


class BannerImagesSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    category = CategorySerializer(many=False)
    competition_participants = serializers.SerializerMethodField()

    # def get_category(self, obj):
    #     return CategorySerializer(obj.category).data

    def get_competition_participants(self, obj):
        request = self.context.get('request')
        return BannerParticipantsSerializer(obj.competition_participants.all()[:3], context={'request': request},
                                            many=True).data

    def get_count(self, obj):
        return obj.competition_participants.count()

    class Meta:
        model = Competition
        fields = ('id', 'title', 'image', 'category', 'distance', 'count', 'competition_participants')


class FutureCompetitionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    last_distance = serializers.CharField(source='competition_maps.title', read_only=True)

    class Meta:
        model = Competition
        fields = ('id', 'title', 'image', 'category', 'last_distance', 'period')


class ParticipantListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_fullname', read_only=True)
    flag = serializers.ImageField(source='user.address.flag', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)

    class Meta:
        model = Participant
        fields = ('id', 'full_name', 'avatar', 'flag', 'personal_id', 'duration')

    def get_smallest_duration(self, participants):
        smallest_duration = None

        for participant in participants:
            duration = participant['duration']
            if duration:
                duration_parts = [int(part) for part in duration.split(':')]
                duration_seconds = duration_parts[0] * 3600 + duration_parts[1] * 60 + duration_parts[2]

                if smallest_duration is None or duration_seconds < smallest_duration:
                    smallest_duration = duration_seconds

        if smallest_duration is not None:
            hours = smallest_duration // 3600
            minutes = (smallest_duration % 3600) // 60
            seconds = smallest_duration % 60
            smallest_duration_formatted = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
            return smallest_duration_formatted
        else:
            return None


class CompetitionMapsListSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()

    def get_participants(self, obj):
        participants = Participant.objects.filter(choice_id=obj.id).order_by('duration')
        return ParticipantListSerializer(participants[:3], many=True).data

    class Meta:
        model = CompetitionMaps
        fields = ('id', 'title', 'participants')


class PastCompetitionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    distances = CompetitionMapsListSerializer(many=True, source='competition_maps')

    class Meta:
        model = Competition
        fields = (
            'id', 'title', 'image', 'category', 'end_date', 'distances')


class ParticipantRetrieveSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_fullname', read_only=True)
    flag = serializers.CharField(source='user.address.flag', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    competition_title = serializers.CharField(source='competition.title', read_only=True)
    competition_image = serializers.ImageField(source='competition.image', read_only=True)
    competition_category = serializers.CharField(source='competition.category.title', read_only=True)
    competition_distance = serializers.CharField(source='choice.title', read_only=True)

    class Meta:
        model = Participant
        fields = (
            'id', 'full_name', 'avatar', 'flag', 'personal_id', 'duration', 'competition_title', 'competition_image',
            'competition_category', 'competition_distance')


class CompetitionMapImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionMaps
        fields = ('id', 'title', 'maps')


class CompetitionDetailSerializer(serializers.ModelSerializer):
    category_icon = serializers.ImageField(source='category.icon', read_only=True)
    participants = serializers.SerializerMethodField()
    competition_texts = CompetitionTextsSerializer(many=True)
    competition_maps = CompetitionMapImagesSerializer(many=True)
    joiners_count = serializers.SerializerMethodField()
    free_joiners_count = serializers.SerializerMethodField()

    def get_joiners_count(self, obj):
        return obj.competition_participants.count()

    def get_free_joiners_count(self, obj):
        if obj.members:
            free_place = obj.members - obj.competition_participants.count()
            return free_place
        return 0

    def get_participants(self, obj):
        participants = Participant.objects.filter(competition_id=obj.id).order_by('duration')
        return ParticipantListSerializer(participants[:3], many=True).data

    class Meta:
        model = Competition
        fields = (
            'id', 'title', 'sub_title', 'youtube', 'media', 'category_icon', 'competition_maps', 'period', 'distance',
            'members', 'joiners_count', 'free_joiners_count',
            'where_is_ticket', 'limit', 'competition_texts', 'participants')


class JoinToCompetitionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ('choice',)
