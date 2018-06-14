modules_values = {
'edata' : '''
            <li class="treeview">
              <a href="{url}">
                <i class="fa fa-credit-card"></i><span>Відкриті фінанси </span>
              </a>
            </li>
            ''',

'igov' : '''
            <li class="treeview">
              <a href="{url}">
                <i class="fa  fa-briefcase"></i> <span>Електронні послуги </span>
              </a>
            </li>
            ''',

'prozorro' : '''
            <li class="treeview">
              <a href="{url}">
                <i class="fa  fa-money"></i> <span>Електронні закупівлі  </span>
              </a>
            </li>
            ''',

'donor' : '''
          	<li class="treeview">
              <a href="{url}">
                <i class="fa fa-heartbeat"></i> <span>Донорство крові </span>
              </a>
            </li>
            ''',

'news' : '''
            <li class="treeview">
              <a href="{url}">
                <i class="fa fa-newspaper-o" data-target="\/news"></i> <span>Новини міста</span>
              </a>
            </li>
            ''',

'defects' : '''
            <li>
              <a href="{url}" >
                <i class="fa fa-search"></i>
                <span>Дефекти ЖКГ</span>
                  {allowed_defects}


            </li>
            ''',

'petitions' : '''
             <li>
                 <a href="{url}" >
                 <i class="fa fa-commenting-o"></i>
                 <span>Петиції</span>
                    {allowed_petitions}


            </li>
            ''',

'polls' : '''
            <li class="treeview">
              <a href="{url}">
                <i class="fa  fa-check"></i> <span>Опитування</span>
              </a>
            </li>
            ''',

'openbudget' : '''
            <li class="treeview">
              <a href="{url}">
                <i class="fa  fa-pie-chart"></i> <span>Відкритий бюджет</span>
              </a>
            </li>
            ''',

'medicine' : '''
            <li class="treeview">
              <a href="{url}">
                <i class="fa fa-edit"></i> <span>Реєстр ліків</span>
              </a>
            </li>
            ''',

'flats' : '''
            <li class="treeview">
              <a href="{url}">
                  <i class="fa fa-users"></i><span>Черги на житло</span>
              </a>
            </li>
        ''',

'smartroads' : '''
            <li>
              <a href="{url}">
                  <i class="fa fa-road"></i><span>Розумні дороги</span>
              </a>
            </li>
            ''',

'mvs_wanted' : '''
            <li class="treeview">
              <a href="{url}">
                  <i class="fa fa-taxi"></i><span>Розшук поліції</span>
              </a>
            </li>
            ''',
}
allowed_petitions = '''
               <i class="fa fa-angle-left pull-right"></i>
               </a>
               <ul class="treeview-menu">
                   <li><a href="/{town_slug}/petitions/add"><i class="fa fa-plus-square-o"></i> Додати петицію</a></li>
                   <li><a href="/{town_slug}/petitions/status/2" ><i class="fa fa-circle-o text-light-blue"></i> Активні петиції</a></li>
                   <li><a href="/{town_slug}/petitions/status/8" ><i class="fa fa-circle-o text-black"></i> На перевірці голосів</a></li>
                   <li><a href="/{town_slug}/petitions/status/6"><i class="fa fa-circle-o text-yellow"></i> Розглядаються</a></li>
                   <li><a href="/{town_slug}/petitions/status/4"><i class="fa fa-circle-o text-green"></i> Розглянуті</a></li>
                   <li><a href="/{town_slug}/petitions/status/3"><i class="fa fa-circle-o text-red"></i> Відхилені</a></li>
                   <li><a href="/{town_slug}/petitions/status/5"><i class="fa fa-circle-o"></i> Архівні</a></li>
                   <li><a href="/{town_slug}/petitions/rules"><i class="fa fa-info"></i> Правила</a></li>
                   <li><a href="/{town_slug}/petitions/help"><i class="fa fa-question-circle"></i> Допомога</a></li>
               </ul>'''

allowed_defects = '''
                <i class="fa fa-angle-left pull-right"></i>
                </a>
                  <ul class="treeview-menu">
                    <li><a href="/{town_slug}/defects/list"><i class="fa fa-th-list"></i> Реєстр заявок</a></li>
                    <li><a href="/{town_slug}/defects/add"><i class="fa fa-plus-square-o"></i> Додати заявку</a></li>
                    <li><a href="/{town_slug}/defects/mydefects"><i class="fa fa-user-secret"></i> Мої заявки</a></li>
                    <li><a href="/{town_slug}/defects/rules"><i class="fa  fa-info"></i> Правила</a></li>
                    <li><a href="/{town_slug}/defects/help"><i class="fa fa-question-circle"></i>Допомога</a></li>
                  </ul>'''
moders_content = '''
            <li >
                 <a href="/{town_slug}/moderators">
                     <i class="fa fa-user"></i> <span>Регіональні модератори</span>
                 </a>
            </li>'''