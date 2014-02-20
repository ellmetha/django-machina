# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Forum'
        db.create_table(u'forum_forum', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name=u'children', null=True, to=orm['forum.Forum'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('machina.models.fields.MarkupTextField')(blank=True, null=True, no_rendered_field=True)),
            ('image', self.gf('machina.models.fields.ExtendedImageField')(max_length=100, null=True, blank=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('link_redirects', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(db_index=True)),
            ('posts_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('topics_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('real_topics_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('link_redirects_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('display_sub_forum_list', self.gf('django.db.models.fields.BooleanField')(default=True)),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'_description_rendered', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'forum', ['Forum'])


    def backwards(self, orm):
        # Deleting model 'Forum'
        db.delete_table(u'forum_forum')


    models = {
        u'forum.forum': {
            'Meta': {'ordering': "[u'tree_id', u'lft']", 'object_name': 'Forum'},
            u'_description_rendered': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('machina.models.fields.MarkupTextField', [], {'blank': 'True', 'null': 'True', u'no_rendered_field': 'True'}),
            'display_sub_forum_list': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('machina.models.fields.ExtendedImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'link_redirects': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'link_redirects_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'children'", 'null': 'True', 'to': u"orm['forum.Forum']"}),
            'posts_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'real_topics_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'topics_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['forum']