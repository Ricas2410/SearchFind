from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0013_company_fields_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='industry',
            field=models.CharField(choices=[('accounting', 'Accounting'), ('advertising', 'Advertising'), ('aerospace', 'Aerospace'), ('agriculture', 'Agriculture'), ('automotive', 'Automotive'), ('banking', 'Banking'), ('biotechnology', 'Biotechnology'), ('construction', 'Construction'), ('consulting', 'Consulting'), ('consumer_goods', 'Consumer Goods'), ('education', 'Education'), ('energy', 'Energy'), ('entertainment', 'Entertainment'), ('fashion', 'Fashion'), ('finance', 'Finance'), ('food_beverage', 'Food & Beverage'), ('government', 'Government'), ('healthcare', 'Healthcare'), ('hospitality', 'Hospitality'), ('insurance', 'Insurance'), ('legal', 'Legal'), ('manufacturing', 'Manufacturing'), ('marketing', 'Marketing'), ('media', 'Media'), ('non_profit', 'Non-Profit'), ('pharmaceutical', 'Pharmaceutical'), ('real_estate', 'Real Estate'), ('retail', 'Retail'), ('technology', 'Technology'), ('telecommunications', 'Telecommunications'), ('transportation', 'Transportation'), ('travel', 'Travel'), ('utilities', 'Utilities'), ('other', 'Other')], max_length=100),
        ),
    ]
